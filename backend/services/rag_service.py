"""
=============================================================================
RAG 业务服务层 (Service Layer)
=============================================================================

【架构中的位置】
这是三层架构中的"业务逻辑层"（Service Layer）：

  Router（路由层）   → 接收 HTTP 请求，参数校验，返回响应
  Service（服务层）  → 业务流程编排，事务管理，数据转换 ← 你在这里
  Model/CRUD（数据层）→ 数据库操作，向量存储操作

【类比 Java 的 Spring 架构】
  Router   = @RestController (@RequestMapping)
  Service  = @Service（事务管理 + 业务逻辑）
  Model    = @Entity + @Repository（JPA Repository）

【本模块的职责】
1. 编排 Ingest/Query 管线的调用
2. 管理 MySQL 中的元数据（知识库、文档、对话）
3. 协调 MySQL 和 Qdrant 的数据一致性
4. ORM 模型 ↔ Pydantic Schema 的数据转换
5. 流式查询的生成器封装
"""

import json
from uuid import uuid4          # 生成唯一 ID（替代数据库自增）
from typing import Optional, List
from datetime import datetime

# SQLAlchemy 2.0 风格：用 select() 函数而非 session.query()
from sqlalchemy import select, func, delete

# SessionLocal = 数据库会话工厂
# 类比 Java 中的 EntityManagerFactory.createEntityManager()
from database.session import SessionLocal

from models.rag import KnowledgeBaseModel, DocumentModel, RAGConversationModel

# Pydantic Schema = 数据传输对象
# 类比 Java 中的 DTO（Data Transfer Object）
from schemas.rag import (
    RAGQueryResponse,
    KnowledgeBase,
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    Document,
    DocumentUploadResponse,
    RAGConversation,
)

from rag.ingest import IngestPipeline
from rag.query import QueryPipeline
from rag.qdrant_store import QdrantStore
from rag.evaluation import evaluate_single_query


class RAGService:
    """
    RAG 业务服务 —— 整个 RAG 系统的"总指挥"。

    【三层协同示例】
    用户上传文档的完整流程：
    1. Router    → 接收 UploadFile，调用 service.upload_document()
    2. Service   → 验证知识库存在 → 写 MySQL 元数据 → 调用 IngestPipeline
    3. Ingest    → Parser → Cleaner → Splitter → BGE-M3 → Qdrant
    4. Service   → 更新 MySQL 中的文档状态 → 清除 BM25 缓存
    5. Router    → 返回 DocumentUploadResponse
    """

    def __init__(self):
        # 组装三个核心组件
        self.ingest_pipeline = IngestPipeline()  # 文档摄入
        self.query_pipeline = QueryPipeline()     # RAG 查询
        self.store = QdrantStore()                 # 向量存储

    # =====================================================================
    # 查询（Query）
    # =====================================================================

    def query(self, question: str, knowledge_base_id: Optional[str] = None, public_only: bool = False) -> RAGQueryResponse:
        """
        非流式 RAG 查询 —— 等待完整答案后返回。
        适合：API 调用、批量评估、不需要实时反馈的场景
        """
        kb_id = knowledge_base_id or self._get_default_kb_id(public_only=public_only)
        
        # 如果指定了 kb_id 且 public_only，需验证可见性
        if public_only and knowledge_base_id:
            kb_info = self.get_knowledge_base_by_id(knowledge_base_id)
            if kb_info and kb_info.visibility != "public":
                from utils.exceptions import NotFoundException
                raise NotFoundException(message="知识库不存在或无权访问", err_code="KB_NOT_FOUND")
        
        result = self.query_pipeline.query(
            question=question,
            kb_id=kb_id,
        )
        return RAGQueryResponse(
            answer=result.answer,
            sources=result.sources,
            confidence=result.confidence,
        )

    def query_stream(self, question: str, knowledge_base_id: Optional[str] = None, public_only: bool = False):
        """
        流式查询 —— 边生成边输出（逐 token 返回）。

        【Python 生成器 yield 原理】
        这是一个生成器函数（generator），类似 Java 的 Iterator：
        - 每次 yield 返回一个 token
        - 调用方用 for...in 逐条消费
        - 不会一次性加载全部结果到内存

        【与 query() 的区别】
        query()    → invoke()  一次性返回完整答案
        query_stream() → stream()  逐个 token 流式返回

        类比：query() = 等整个 HTTP 响应下载完再读取
              query_stream() = 边下载边播放视频

        【为什么流式查询里重复了检索逻辑】
        因为 LLM 的 stream() 返回的是迭代器，不方便封装到 QueryPipeline.
        query() 方法中（返回 str）。这里直接内联实现了完整流程。
        这是有意的代码重复——流式和非流式的调用链差异太大，
        强行合并反而会让代码难以理解。
        """
        from langchain_core.messages import HumanMessage, SystemMessage

        # 检索阶段：Query 改写 + 多查询检索合并
        rewritten = self.query_pipeline.rewriter.rewrite(question)
        kb_id = knowledge_base_id or self._get_default_kb_id(public_only=public_only)

        all_candidates: dict[str, dict] = {}
        for search_query in rewritten.search_queries:
            try:
                qv = self.query_pipeline.embedder.embed_query(search_query)
                candidates = self.query_pipeline._hybrid_retrieval(
                    kb_id=kb_id,
                    query_text=search_query,
                    query_vector=qv,
                    top_k=10,
                )
                for item in candidates:
                    text = item.get("text", "")
                    if text and (text not in all_candidates or item.get("score", 0) > all_candidates[text].get("score", 0)):
                        all_candidates[text] = item
            except Exception:
                continue

        merged = list(all_candidates.values())
        candidate_texts = [c["text"] for c in merged]
        reranked = self.query_pipeline.reranker.rerank(rewritten.original, candidate_texts, top_k=5)
        context_parts = [doc for _, doc, _ in reranked]

        # 构建 Prompt
        system_prompt = (
            "你是一个专业的知识问答助手。请根据提供的参考资料回答问题。"
            "要求：简洁、准确、有条理。使用中文回答。"
        )
        context_text = "\n\n---\n\n".join(context_parts) if context_parts else "无参考资料。"
        user_prompt = f"参考资料：\n{context_text}\n\n问题：{question}\n\n请基于以上参考资料回答问题。"

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        # 流式生成：逐个 token yield
        for chunk in self.query_pipeline.llm.stream(messages):
            if hasattr(chunk, "content") and chunk.content:
                yield chunk.content

    # =====================================================================
    # 知识库 CRUD
    # =====================================================================

    def get_knowledge_bases(self, public_only: bool = False) -> List[KnowledgeBase]:
        """
        获取所有知识库列表。

        SQL 等价：SELECT * FROM knowledge_bases ORDER BY created_at DESC;

        【with SessionLocal() as db 的含义】
        Python 上下文管理器（context manager），类似 Java 的 try-with-resources：
            try (Session session = sessionFactory.openSession()) {
                // 自动关闭连接
            }
        """
        with SessionLocal() as db:
            # SQLAlchemy 2.0 风格：select() 而非 session.query()
            stmt = select(KnowledgeBaseModel)
            if public_only:
                stmt = stmt.where(KnowledgeBaseModel.visibility == "public")
            rows = db.execute(
                stmt.order_by(KnowledgeBaseModel.created_at.desc())
            ).scalars().all()
            # ORM 对象 → Pydantic Schema（适配 API 响应格式）
            return [self._kb_to_schema(row) for row in rows]

    def get_knowledge_base_by_id(self, kb_id: str) -> Optional[KnowledgeBase]:
        """
        按 kb_id 查询单个知识库。

        SQL 等价：SELECT * FROM knowledge_bases WHERE kb_id = :kb_id;

        scalar_one_or_none()：
        - 找到 0 条 → 返回 None
        - 找到 1 条 → 返回该对象
        - 找到多条 → 抛异常（因为 kb_id 是 UNIQUE 的，不应该发生）
        """
        with SessionLocal() as db:
            row = db.execute(
                select(KnowledgeBaseModel).where(KnowledgeBaseModel.kb_id == kb_id)
            ).scalar_one_or_none()
            return self._kb_to_schema(row) if row else None

    def create_knowledge_base(self, kb_create: KnowledgeBaseCreate) -> KnowledgeBase:
        """
        创建新知识库。

        SQL 等价：
            INSERT INTO knowledge_bases (kb_id, name, description, ...) VALUES (...);

        【UUID vs 自增 ID】
        我们用 uuid4() 生成 kb_id（对外标识），让 MySQL 用自增 id（内部关联）。
        好处：
        - API 中的 ID 不可预测（/api/kb/abc123 而非 /api/kb/1），防遍历
        - 如果以后分库分表，UUID 不会冲突
        """
        now = datetime.now()
        kb_id = str(uuid4())

        with SessionLocal() as db:
            kb = KnowledgeBaseModel(
                kb_id=kb_id,
                name=kb_create.name,
                description=kb_create.description,
                is_default=kb_create.is_default or False,
                created_at=now,
                updated_at=now,
            )
            db.add(kb)       # 加入会话
            db.commit()      # 提交事务（INSERT 真正执行）
            db.refresh(kb)   # 刷新获取数据库生成的值（如自增 id）
            return self._kb_to_schema(kb)

    def update_knowledge_base(self, kb_id: str, kb_update: KnowledgeBaseUpdate) -> Optional[KnowledgeBase]:
        """
        部分更新知识库。

        SQL 等价：
            UPDATE knowledge_bases SET name=?, description=?, ... WHERE kb_id=?;

        【部分更新 vs 全量更新】
        KnowledgeBaseUpdate 的所有字段都是 Optional，
        前端可以只传要修改的字段（PATCH 语义）。
        未传的字段保持原值不变。
        """
        with SessionLocal() as db:
            row = db.execute(
                select(KnowledgeBaseModel).where(KnowledgeBaseModel.kb_id == kb_id)
            ).scalar_one_or_none()
            if not row:
                return None

            # 只更新传入的字段
            if kb_update.name is not None:
                row.name = kb_update.name
            if kb_update.description is not None:
                row.description = kb_update.description
            if kb_update.is_default is not None:
                row.is_default = kb_update.is_default
            row.updated_at = datetime.now()

            db.commit()
            db.refresh(row)
            return self._kb_to_schema(row)

    def delete_knowledge_base(self, kb_id: str) -> bool:
        """
        删除知识库 —— 级联删除关联数据。

        删除顺序（参照 MySQL 外键约束的 CASCADE 逻辑）：
        1. 删除关联的文档元数据（MySQL）
        2. 删除关联的对话记录（MySQL）
        3. 删除知识库本身（MySQL）
        4. 删除 Qdrant Collection（向量数据）
        5. 清除 BM25 缓存

        【为什么手动级联】
        SQLAlchemy 也可以配置 cascade="all, delete-orphan"，
        但 Qdrant 的删除无法自动级联（不在同一数据库），
        所以统一手动处理所有步骤，逻辑更清晰可见。
        """
        with SessionLocal() as db:
            row = db.execute(
                select(KnowledgeBaseModel).where(KnowledgeBaseModel.kb_id == kb_id)
            ).scalar_one_or_none()
            if not row:
                return False

            # 级联删除关联文档
            db.execute(
                delete(DocumentModel).where(DocumentModel.knowledge_base_id == row.id)
            )
            # 级联删除关联对话
            db.execute(
                delete(RAGConversationModel).where(RAGConversationModel.knowledge_base_id == row.id)
            )
            db.delete(row)
            db.commit()

        # 删除 Qdrant 中的向量数据
        self.store.delete_collection(kb_id)
        # 清除该 KB 的 BM25 缓存
        self.query_pipeline.clear_bm25_cache(kb_id)
        return True

    # =====================================================================
    # 文档管理
    # =====================================================================

    def upload_document(
        self,
        kb_id: str,
        filename: str,
        content: bytes,
        mime_type: str = "",
    ) -> DocumentUploadResponse:
        """
        上传文档并自动执行完整 ingest 管线。

        这是"上传即处理"的设计：用户上传文件 → 系统自动解析、清洗、
        切分、向量化、存储。前端可以轮询文档状态查看进度。

        【流程】
        1. 验证知识库存在
        2. 在 MySQL 中创建文档记录（status="processing"）
        3. 调用 IngestPipeline 执行完整摄入
        4. 根据摄入结果更新文档状态（completed / failed）
        5. 清除 BM25 缓存（因为数据变了）
        """
        # 验证知识库存在
        kb = self.get_knowledge_base_by_id(kb_id)
        if not kb:
            return DocumentUploadResponse(
                message=f"知识库 {kb_id} 未找到",
                document_id=None,
            )

        doc_id = str(uuid4())
        now = datetime.now()

        # 先写元数据（状态标记为 processing）
        with SessionLocal() as db:
            kb_row = db.execute(
                select(KnowledgeBaseModel).where(KnowledgeBaseModel.kb_id == kb_id)
            ).scalar_one()

            doc = DocumentModel(
                doc_id=doc_id,
                knowledge_base_id=kb_row.id,
                filename=filename,
                file_type=mime_type,
                file_size=len(content),
                status="processing",  # 状态：处理中
                chunk_count=0,
                created_at=now,
            )
            db.add(doc)
            db.commit()

        # 执行 ingest 管线（这一步可能耗时数秒到数十秒）
        result = self.ingest_pipeline.ingest(
            kb_id=kb_id,
            doc_id=doc_id,
            content=content,
            filename=filename,
            mime_type=mime_type,
        )

        # 更新文档状态
        with SessionLocal() as db:
            doc_row = db.execute(
                select(DocumentModel).where(DocumentModel.doc_id == doc_id)
            ).scalar_one()
            if result.success:
                doc_row.status = "completed"
                doc_row.chunk_count = result.chunk_count
            else:
                doc_row.status = "failed"
            db.commit()

        # 重建 BM25 索引（新文档已入库，索引需要更新）
        self.query_pipeline.clear_bm25_cache(kb_id)

        if result.success:
            return DocumentUploadResponse(
                message=f"文档上传成功，已切分为 {result.chunk_count} 个 chunk",
                document_id=doc_id,
            )
        else:
            return DocumentUploadResponse(
                message=f"文档处理失败：{result.error}",
                document_id=doc_id,
            )

    def get_documents(self, kb_id: Optional[str] = None) -> List[Document]:
        """
        获取文档列表（可选的按知识库过滤）。

        【参数设计】
        kb_id=None：返回所有文档
        kb_id="xxx"：只返回该知识库的文档
        """
        with SessionLocal() as db:
            stmt = select(DocumentModel)
            if kb_id:
                # 先查知识库的内部 id
                kb_row = db.execute(
                    select(KnowledgeBaseModel).where(KnowledgeBaseModel.kb_id == kb_id)
                ).scalar_one_or_none()
                if kb_row:
                    stmt = stmt.where(DocumentModel.knowledge_base_id == kb_row.id)

            stmt = stmt.order_by(DocumentModel.created_at.desc())
            rows = db.execute(stmt).scalars().all()
            return [self._doc_to_schema(row) for row in rows]

    def delete_document(self, doc_id: str) -> bool:
        """
        删除文档 —— 同时清除 MySQL 元数据和 Qdrant 向量。

        【数据一致性保证】
        1. 先从 MySQL 查出文档所属的知识库 kb_id
        2. 从 MySQL 删除文档记录
        3. 从 Qdrant 删除对应 chunks
        4. 清除 BM25 缓存

        如果第 3 步失败（Qdrant 宕机），MySQL 已删但向量还在。
        对个人网站来说可接受——不会造成功能错误，只是多了点"孤儿向量"。
        如果需要严格保证，可以考虑分布式事务（Saga 模式），但这里没必要。
        """
        with SessionLocal() as db:
            row = db.execute(
                select(DocumentModel).where(DocumentModel.doc_id == doc_id)
            ).scalar_one_or_none()
            if not row:
                return False

            # 反向查知识库的 kb_id
            kb_row = db.execute(
                select(KnowledgeBaseModel).where(KnowledgeBaseModel.id == row.knowledge_base_id)
            ).scalar_one()
            kb_id = kb_row.kb_id

            db.delete(row)
            db.commit()

        # 删除 Qdrant 中的向量
        self.ingest_pipeline.remove_document(kb_id, doc_id)
        self.query_pipeline.clear_bm25_cache(kb_id)
        return True

    # =====================================================================
    # 对话记录
    # =====================================================================

    def get_conversations(self, kb_id: Optional[str] = None) -> List[RAGConversation]:
        """获取对话历史（可选的按知识库过滤）。"""
        with SessionLocal() as db:
            stmt = select(RAGConversationModel)
            if kb_id:
                kb_row = db.execute(
                    select(KnowledgeBaseModel).where(KnowledgeBaseModel.kb_id == kb_id)
                ).scalar_one_or_none()
                if kb_row:
                    stmt = stmt.where(RAGConversationModel.knowledge_base_id == kb_row.id)

            stmt = stmt.order_by(RAGConversationModel.created_at.desc())
            rows = db.execute(stmt).scalars().all()
            return [self._conv_to_schema(row) for row in rows]

    def evaluate_query(
        self,
        question: str,
        kb_id: Optional[str] = None,
        ground_truth: Optional[str] = None,
    ) -> dict:
        """
        评估单次 RAG 查询。
        
        执行查询 → 获取 answer + contexts → 调用 RAGAS 评估。
        """
        # 1. 执行查询
        response = self.query(question, kb_id)
        
        # 2. 获取检索到的 contexts（来源文档 ID 列表→需要转为文本）
        # sources 是 doc_id 列表，contexts 需要是文本片段
        contexts = response.sources if response.sources else []
        
        # 3. 调用评估
        eval_result = evaluate_single_query(
            question=question,
            answer=response.answer,
            contexts=contexts,
            ground_truth=ground_truth or "",
        )
        return eval_result

    def save_conversation(
        self,
        kb_id: Optional[str],
        user_query: str,
        answer: str,
        sources: List[str],
    ) -> RAGConversation:
        """
        保存对话记录。

        每次 RAG 查询后自动调用，记录问答对和引用来源。
        后续可用于：展示对话历史、分析提问趋势、优化知识库。
        """
        conv_id = str(uuid4())
        now = datetime.now()

        with SessionLocal() as db:
            # 将 kb_id（对外 UUID）转为内部 id（数据库主键）
            kb_pk = None
            if kb_id:
                kb_row = db.execute(
                    select(KnowledgeBaseModel).where(KnowledgeBaseModel.kb_id == kb_id)
                ).scalar_one_or_none()
                if kb_row:
                    kb_pk = kb_row.id

            conv = RAGConversationModel(
                conversation_id=conv_id,
                knowledge_base_id=kb_pk,
                user_query=user_query,
                answer=answer,
                # json.dumps 确保 sources 以合法 JSON 字符串存入数据库
                # ensure_ascii=False 保留中文字符不转义
                sources=json.dumps(sources, ensure_ascii=False),
                created_at=now,
            )
            db.add(conv)
            db.commit()
            db.refresh(conv)
            return self._conv_to_schema(conv)

    # =====================================================================
    # 辅助方法
    # =====================================================================

    def _get_default_kb_id(self, public_only: bool = False) -> str:
        """获取默认知识库的 kb_id，优先选有 Qdrant 数据的 KB。"""
        with SessionLocal() as db:
            # 1. 优先：标记为默认的知识库
            stmt = select(KnowledgeBaseModel).where(KnowledgeBaseModel.is_default == True)
            if public_only:
                stmt = stmt.where(KnowledgeBaseModel.visibility == "public")
            row = db.execute(stmt.limit(1)).scalar_one_or_none()
            if row and self.store.collection_exists(row.kb_id):
                return row.kb_id
            # 2. 回退：找有 Qdrant 数据的最早 KB
            stmt2 = select(KnowledgeBaseModel).order_by(KnowledgeBaseModel.created_at.asc())
            if public_only:
                stmt2 = stmt2.where(KnowledgeBaseModel.visibility == "public")
            rows = db.execute(stmt2).scalars().all()
            for r in rows:
                if self.store.collection_exists(r.kb_id):
                    return r.kb_id
            # 3. 兜底：返回第一个（即使无数据）
            if rows:
                return rows[0].kb_id
            return "default"
    # =====================================================================
    # ORM → Schema 映射（类似 Java 中的 BeanUtils.copyProperties）
    # =====================================================================

    def _kb_to_schema(self, row: KnowledgeBaseModel) -> KnowledgeBase:
        """
        SQLAlchemy ORM 对象 → Pydantic 响应 Schema。

        这里做了一层"隔离"：
        - 数据库的 id（自增主键）不暴露给 API
        - kb_id（对外 UUID）作为 API 中的 id 字段

        类比 Java 中 Entity → DTO 的转换。
        """
        return KnowledgeBase(
            id=row.kb_id,
            name=row.name,
            description=row.description,
            is_default=row.is_default,
            visibility=row.visibility or "private",
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    def _doc_to_schema(self, row: DocumentModel) -> Document:
        """文档 ORM → Schema 映射"""
        return Document(
            id=row.doc_id,
            knowledge_base_id=str(row.knowledge_base_id),
            filename=row.filename,
            file_type=row.file_type or "",
            file_size=row.file_size,
            status=row.status,
            chunk_count=row.chunk_count,
            created_at=row.created_at,
        )

    def _conv_to_schema(self, row: RAGConversationModel) -> RAGConversation:
        """
        对话 ORM → Schema 映射。

        sources 在数据库中是 JSON 字符串，这里反序列化为 Python List。
        """
        sources = []
        if row.sources:
            try:
                sources = json.loads(row.sources)
            except (json.JSONDecodeError, TypeError):
                pass  # 解析失败则返回空列表

        return RAGConversation(
            id=row.conversation_id,
            knowledge_base_id=str(row.knowledge_base_id) if row.knowledge_base_id else None,
            user_query=row.user_query,
            answer=row.answer,
            sources=sources,
            created_at=row.created_at,
        )
