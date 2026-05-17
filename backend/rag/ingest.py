"""
=============================================================================
RAG 核心模块 — Ingest 管线 (Ingest Pipeline)
=============================================================================

【RAG 概念入门】
Ingest（摄入）= 把外部文档"消化"到知识库中的完整流水线。
这是 RAG 系统的"写入"路径，对应 CRUD 中的 C（Create）。

【管线五阶段】
  📄 原始文件（PDF/Word/MD...）
     │
     ▼ Parser（解析）
  📝 纯文本 + 标题
     │
     ▼ Cleaner（清洗）
  ✨ 干净文本（去 HTML、URL、控制字符）
     │
     ▼ Splitter（切分）
  📦 Chunk 列表（每段约 500 字，50 字重叠）
     │
     ▼ Embedding（向量化）
  🔢 向量列表（每个 chunk → 1024 维向量）
     │
     ▼ Qdrant（存储）
  💾 存入向量数据库，可被检索

【类比数据管道】
就像把 CSV 文件导入 MySQL 的 ETL 管道：
  CSV → 字段解析 → 数据清洗 → 类型转换 → INSERT INTO table

本模块是"指挥官"角色——不自己做具体工作，而是编排各模块的执行顺序。
"""

from typing import List
from dataclasses import dataclass, field

from .parser import DocumentParser, ParsedDocument
from .cleaner import DocumentCleaner
from .splitter import TextSplitter
from .monitor import timed, reset_timing_ctx
from .embedding import EmbeddingService
from .qdrant_store import QdrantStore


@dataclass
class IngestResult:
    """
    摄入操作的结果。

    成功时：success=True，返回 chunk 数量和 ID 列表
    失败时：success=False，error 字段包含失败原因

    类比 Java 的 Result<T, E> 或 Go 的 (result, error) 模式。
    """
    success: bool
    kb_id: str           # 目标知识库 ID
    doc_id: str          # 文档 ID
    chunk_count: int = 0      # 切分出多少个 chunk
    chunk_ids: List[str] = field(default_factory=list)  # 每个 chunk 的 UUID
    error: str = ""           # 失败时的错误信息


class IngestPipeline:
    """
    文档摄入管线 —— 编排者（Orchestrator）。

    【设计模式：管线模式（Pipeline Pattern）】
    每个阶段是独立的处理单元，前一阶段的输出是后一阶段的输入。
    如果任一阶段失败，整个管线中止并返回错误。

    【为何要拆分阶段】
    1. 可测试：每个阶段可独立单元测试
    2. 可替换：如果以后换一个更好的 PDF 解析器，只改 Parser 模块即可
    3. 可复用：Cleaner 同样可以用于其他数据源（爬虫、API 等）
    """

    def __init__(self):
        # 组装管线各阶段
        self.parser = DocumentParser()
        self.cleaner = DocumentCleaner()
        self.splitter = TextSplitter()
        self.embedder = EmbeddingService()
        self.store = QdrantStore()

    @timed("ingest_total")
    def ingest(
        self,
        kb_id: str,
        doc_id: str,
        content: bytes,
        filename: str,
        mime_type: str = "",
    ) -> IngestResult:
        """
        执行完整摄入流程：解析 → 清洗 → 切分 → 向量化 → 存储。

        【整体 try-except 的原因】
        管线中任何一步都可能失败：
        - PDF 损坏 → pypdf 抛异常
        - 文本为空 → 提前返回错误
        - BGE-M3 加载失败 → 模型文件损坏
        - Qdrant 连接断开 → 网络异常

        用最外层 try-except 兜底，确保永远返回 IngestResult
        而不是让未捕获的异常炸掉整个请求。

        【Args 说明】
        kb_id:    知识库 ID（对应 Qdrant Collection）
        doc_id:   文档 ID（UUID，用于后续追溯和删除）
        content:  文件的原始字节（从 FastAPI UploadFile 读取）
        filename: 原始文件名
        mime_type: HTTP Content-Type
        """
        try:
            # ─── 阶段 1：解析（Extract）───
            # 把不同格式的文件统一转成纯文本
            from .monitor import get_timing_ctx
            _ctx = get_timing_ctx()
            import time as _time
            
            _t0 = _time.perf_counter()
            parsed: ParsedDocument = self.parser.parse(content, filename, mime_type)
            _ctx.record("parser_parse", (_time.perf_counter() - _t0) * 1000)

            # ─── 阶段 2：清洗（Transform）───
            # 去除 HTML 标签、URL、控制字符等噪音
            _t0 = _time.perf_counter()
            cleaned: str = self.cleaner.clean(parsed.text)
            _ctx.record("cleaner_clean", (_time.perf_counter() - _t0) * 1000)
            if not cleaned.strip():
                _ctx.flush()
                return IngestResult(
                    success=False, kb_id=kb_id, doc_id=doc_id,
                    error="文档解析后内容为空，可能是损坏的文件或不支持的格式",
                )

            # ─── 阶段 3：切分（Split）───
            # 将长文档切成多个语义 chunk
            _t0 = _time.perf_counter()
            chunks: List[str] = self.splitter.split(cleaned)
            _ctx.record("splitter_split", (_time.perf_counter() - _t0) * 1000)

            # ─── 阶段 4：向量化（Embed）───
            # 每个 chunk 转成 1024 维向量，批量处理
            _t0 = _time.perf_counter()
            embeddings = self.embedder.embed_documents(chunks)
            _ctx.record("embed_documents", (_time.perf_counter() - _t0) * 1000)

            # ─── 阶段 5：确保 Collection 存在 ───
            # 类似 CREATE TABLE IF NOT EXISTS
            # 传入 self.embedder.dim（1024）确保维度匹配
            self.store.ensure_collection(kb_id, self.embedder.dim)

            # ─── 阶段 6：写入 Qdrant（Load）───
            # 把向量和元数据批量写入向量数据库
            chunk_data = [
                {
                    "text": chunk,
                    "embedding": emb,
                    "doc_id": doc_id,
                    "chunk_index": i,
                }
                for i, (chunk, emb) in enumerate(zip(chunks, embeddings))
            ]
            _t0 = _time.perf_counter()
            chunk_ids = self.store.upsert_chunks(kb_id, chunk_data)
            _ctx.record("qdrant_upsert", (_time.perf_counter() - _t0) * 1000)

            _ctx.flush()
            return IngestResult(
                success=True,
                kb_id=kb_id,
                doc_id=doc_id,
                chunk_count=len(chunks),
                chunk_ids=chunk_ids,
            )

        except Exception as e:
            # 兜底错误处理
            _ctx.flush()
            return IngestResult(
                success=False,
                kb_id=kb_id,
                doc_id=doc_id,
                error=f"摄入流程异常: {type(e).__name__}: {str(e)}",
            )

    def remove_document(self, kb_id: str, doc_id: str) -> None:
        """
        从 Qdrant 中删除某文档的所有 chunks。

        使用场景：用户在前端删除已上传的文档。
        """
        self.store.delete_by_doc_id(kb_id, doc_id)
