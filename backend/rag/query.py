"""
=============================================================================
RAG 核心模块 — Query 管线 (Query Pipeline)
=============================================================================

【RAG 概念入门】
这是 RAG 系统的"读取"路径，也是最核心的功能。
当用户提问时，经过以下步骤生成答案：

  用户提问: "什么是 RAG？"
     │
     ▼ ① Query 向量化
  [0.12, -0.34, 0.56, ...]  (1024维)
     │
     ├──→ ②a 向量检索 (Qdrant) ──→ Top-20 候选
     │
     └──→ ②b BM25 关键字检索 ──→ Top-20 候选
     │
     ▼ ③ RRF 融合（合并两个召回通道的结果）
  Top-10 融合结果
     │
     ▼ ④ BGE-Reranker 重排序（精排）
  Top-5 最相关文档片段
     │
     ▼ ⑤ Prompt 组装
  System: "你是知识问答助手..."
  User:   "参考资料: ...\n问题: ..."
     │
     ▼ ⑥ DeepSeek-V4 生成
  "RAG 是一种结合信息检索和文本生成的技术..."

【核心概念：混合检索 + RRF 融合】

为什么需要两路检索？
- 向量检索：擅长语义匹配。"苹果手机"→"iPhone" 虽然字面不同但意义相近
- BM25 检索：擅长关键字匹配。"API_KEY" 不会被向量检索"软化"掉

两者互补。RRF（Reciprocal Rank Fusion）是一种经典融合方法：
对每个文档，计算它在两路结果中的排名的倒数之和作为最终分数。
排第 1 名得分 1/(60+1)，排第 10 名得分 1/(60+10)，让"两路都高"的文档胜出。

【类比搜索引擎】
- 向量检索 = Google 的语义搜索
- BM25 = 传统的 TF-IDF 关键字匹配
- RRF = 把两个排序结果合并成一个综合排序
"""

from typing import List, Optional
from dataclasses import dataclass, field
from collections import OrderedDict

# LangChain 封装：ChatOpenAI = 任何兼容 OpenAI 接口的 LLM
# DeepSeek API 完全兼容 OpenAI SDK，所以可以直接用 ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from .embedding import EmbeddingService
from .reranker import RerankerService
from .qdrant_store import QdrantStore
from core.config import settings


@dataclass
class QueryResult:
    """
    查询结果数据结构。

    - answer:     LLM 生成的最终答案
    - sources:    引用的文档 ID 列表（用于前端展示"参考来源"）
    - confidence: 置信度（Reranker 最高分，0~1）
    """
    answer: str
    sources: List[str] = field(default_factory=list)
    confidence: float = 0.0


class QueryPipeline:
    """
    RAG 查询管线 —— 整个系统最核心的模块。

    【初始化说明】
    - embedder/reranker/store：复用已加载的单例模型
    - _llm：懒加载 DeepSeek-V4 客户端
    - _bm25_cache：BM25 索引的本地缓存，避免每次查询都重建
      {kb_id: (all_texts_list, BM25Okapi_instance)}
    """

    def __init__(self):
        self.embedder = EmbeddingService()
        self.reranker = RerankerService()
        self.store = QdrantStore()
        self._llm: ChatOpenAI | None = None
        # BM25 缓存：key=知识库ID, value=(原文列表, BM25索引对象)
        self._bm25_cache: dict[str, tuple[list[str], object]] = {}

    @property
    def llm(self) -> ChatOpenAI:
        """
        DeepSeek-V4 大模型客户端（懒加载）。

        【配置说明】
        - model="deepseek-chat"：DeepSeek 的聊天模型标识
        - api_key：从 .env 读取，必须在环境变量中配置
        - base_url：API 地址，默认为 https://api.deepseek.com
        - temperature=0.3：控制生成随机性
          * 0.0 = 完全确定性（适合事实型问答）
          * 0.3 = 轻微随机性（保留一点表达多样性）
          * 1.0+ = 高度随机（创意写作）

        类比：temperature 就像 SQL 查询的"要不要加随机排序"
        0.0 = ORDER BY relevance DESC —— 每次结果一样
        1.0 = ORDER BY RAND() —— 每次结果可能不同
        """
        if self._llm is None:
            self._llm = ChatOpenAI(
                model="deepseek-chat",
                api_key=settings.DEEPSEEK_API_KEY,
                base_url=settings.DEEPSEEK_BASE_URL,
                temperature=0.3,
            )
        return self._llm

    # =====================================================================
    # 主入口：完整 RAG 查询
    # =====================================================================

    def query(
        self,
        question: str,
        kb_id: Optional[str] = None,
        top_k: int | None = None,
    ) -> QueryResult:
        """
        完整 RAG 查询的入口方法。

        走完整个管线的 6 个阶段，返回最终答案。

        【流程概览】
        ① 向量化问题
        ② 混合检索（向量 + BM25 + RRF 融合）
        ③ 重排序（BGE-Reranker 精排 Top-N）
        ④ 构建 Prompt（System Prompt + 参考资料 + 问题）
        ⑤ LLM 生成答案
        ⑥ 封装返回结果

        【无检索结果时的处理】
        如果知识库为空或检索不到相关内容，直接用 LLM 回答（不提供参考资料）。
        这时 confidence=0.0，表示答案未基于私有知识库。
        """
        retrieval_k = top_k or settings.RETRIEVAL_TOP_K  # 默认 10

        # ─── ① Query 向量化 ───
        # 把用户问题转成 1024 维向量（和文档 chunk 在同一空间）
        query_vector = self.embedder.embed_query(question)

        # ─── ② 混合检索 ───
        # 两大召回通道 + RRF 融合
        candidates = self._hybrid_retrieval(
            kb_id=kb_id or "default",
            query_text=question,
            query_vector=query_vector,
            top_k=retrieval_k,
        )

        # 无检索结果 → 直接回答
        if not candidates:
            answer = self._generate_direct(question)
            return QueryResult(answer=answer, sources=[], confidence=0.0)

        # 提取候选文本（用于 reranker）
        candidate_texts = [c["text"] for c in candidates]

        # ─── ③ 重排序 ───
        # 对候选做精排，从 10 个中选出最相关的 5 个
        reranked = self.reranker.rerank(
            question, candidate_texts,
            top_k=settings.RERANK_TOP_K,  # 默认 5
        )

        # 整理重排序结果
        top_docs: list[tuple[str, float]] = []
        for idx, doc, score in reranked:
            top_docs.append((doc, score))

        if not top_docs:
            answer = self._generate_direct(question)
            return QueryResult(answer=answer, sources=[], confidence=0.0)

        # ─── ④ 上下文构建 + ⑤ LLM 生成 ───
        # 用 OrderedDict.fromkeys 去重且保持顺序
        # 相当于 Java 的 LinkedHashSet
        context_parts = [doc for doc, _ in top_docs]
        sources = list(OrderedDict.fromkeys(
            c.get("doc_id", "") for c in candidates
        ))
        confidence = top_docs[0][1] if top_docs else 0.0
        answer = self._generate(question, context_parts)

        # ─── ⑥ 返回结果 ───
        return QueryResult(
            answer=answer,
            sources=sources[:settings.RERANK_TOP_K],
            confidence=round(confidence, 4),
        )

    # =====================================================================
    # 混合检索：向量 + BM25 + RRF 融合
    # =====================================================================

    def _hybrid_retrieval(
        self,
        kb_id: str,
        query_text: str,
        query_vector: List[float],
        top_k: int,
    ) -> List[dict]:
        """
        混合检索（Hybrid Retrieval）—— RAG 检索的核心策略。

        【为什么要两路检索】
        向量检索和 BM25 各有所长，互补使用：

        ┌────────────┬──────────────────┬──────────────────┐
        │            │   向量检索       │   BM25 关键字    │
        ├────────────┼──────────────────┼──────────────────┤
        │ 擅长       │ 语义相似         │ 精确匹配         │
        │ 例         │ "苹果手机"→"iPhone"│ "API_KEY_123"   │
        │ 弱点       │ 长尾专有名词     │ 同义词/近义词    │
        └────────────┴──────────────────┴──────────────────┘

        【为什么各取 top_k * 2】
        给 RRF 融合阶段更多的候选（20 个），融合后再截取 top_k（10 个）。
        这样不会漏掉"向量排名低但 BM25 排名高"的文档。
        """
        # 向量检索：Qdrant HNSW 近似最近邻搜索
        vector_results = self.store.search(kb_id, query_vector, top_k=top_k * 2)

        # BM25 关键字检索：本地内存中的倒排索引
        bm25_results = self._bm25_search(kb_id, query_text, top_k=top_k * 2)

        # 如果 BM25 不可用（rank_bm25 未安装或索引为空），退回纯向量检索
        if not bm25_results:
            return vector_results[:top_k]

        # RRF 融合两路结果
        return self._rrf_fusion(vector_results, bm25_results, k=60, top_k=top_k)

    # =====================================================================
    # BM25 关键字检索
    # =====================================================================

    def _bm25_search(
        self,
        kb_id: str,
        query_text: str,
        top_k: int,
    ) -> List[dict]:
        """
        BM25 关键字检索。

        【BM25 是什么】
        TF-IDF 的升级版，经典的文本相关性算法：
        - TF（词频）：某词在文档中出现次数越多，越相关
        - IDF（逆文档频率）：某词在所有文档中越稀有，权重越高
        - BM25 加入了文档长度归一化，避免长文档天然占优

        类比：MySQL 的 MATCH...AGAINST 全文索引就是类似的实现。

        【为什么缓存在内存中】
        BM25 需要扫描所有 chunk 建索引。每次查询都从 Qdrant 全量 scroll
        出来再建索引太慢。所以首次查询时建好索引并缓存，后续直接复用。

        代价：文档新增/删除后需要清除缓存重建（见 clear_bm25_cache）。
        """
        try:
            from rank_bm25 import BM25Okapi
        except ImportError:
            # rank_bm25 未安装时优雅降级（纯向量检索也能用）
            return []

        # 如果缓存中没有该 KB 的索引，从 Qdrant 加载所有 chunk 文本并建索引
        if kb_id not in self._bm25_cache:
            self._rebuild_bm25_index(kb_id)

        all_chunks, bm25 = self._bm25_cache.get(kb_id, ([], None))
        if not all_chunks or bm25 is None:
            return []

        # 分词（简单空格分词，对中文效果有限但可接受）
        # 更优方案：用 jieba 分词后再建 BM25 索引
        tokenized_query = query_text.split()
        scores = bm25.get_scores(tokenized_query)

        # 按分数降序排列，取 top_k
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)

        return [
            {"text": all_chunks[i], "score": float(score), "doc_id": ""}
            for i, score in ranked[:top_k]
        ]

    def _rebuild_bm25_index(self, kb_id: str) -> None:
        """
        重建 BM25 索引。

        从 Qdrant 中取出该 KB 的所有 chunk 文本，分词后建 BM25 索引。
        全量加载时间复杂度 O(N)，N=该 KB 的 chunk 总数。
        对于个人网站规模（数千~数万 chunk），完全可接受。
        """
        try:
            from rank_bm25 import BM25Okapi
        except ImportError:
            return

        all_texts = self._get_all_chunk_texts(kb_id)
        if all_texts:
            # 分词并建索引
            tokenized = [text.split() for text in all_texts]
            self._bm25_cache[kb_id] = (all_texts, BM25Okapi(tokenized))

    def _get_all_chunk_texts(self, kb_id: str) -> List[str]:
        """
        从 Qdrant 分页获取 KB 中所有 chunk 的文本。

        Qdrant 的 scroll 类似 MySQL 的游标分页：
        - limit=1000：每次取 1000 条
        - offset：从上次的偏移位置继续
        - 返回 (records, next_offset)：next_offset=None 表示已全部读取
        """
        name = self.store.collection_name(kb_id)
        client = self.store.client
        if not client.collection_exists(name):
            return []

        texts: list[str] = []
        offset = None
        while True:
            records, next_offset = client.scroll(
                collection_name=name,
                limit=1000,          # 每页 1000 条
                offset=offset,
                with_payload=["text"],  # 只取 text 字段，节省带宽
                with_vectors=False,     # 不需要向量数据
            )
            for record in records:
                if record.payload and "text" in record.payload:
                    texts.append(record.payload["text"])
            if next_offset is None:  # 没有下一页了
                break
            offset = next_offset
        return texts

    # =====================================================================
    # RRF 融合算法
    # =====================================================================

    def _rrf_fusion(
        self,
        vector_results: List[dict],
        bm25_results: List[dict],
        k: int = 60,
        top_k: int = 10,
    ) -> List[dict]:
        """
        Reciprocal Rank Fusion（倒数排名融合）。

        【为什么用 RRF】
        向量检索和 BM25 检索返回的分数不在同一尺度上：
        - 向量检索返回余弦相似度 (0~1)
        - BM25 返回 TF-IDF 分数 (0~数十)
        不能直接相加。

        RRF 绕过这个问题：不看原始分数，只看排名。
        公式：score(doc) = Σ 1/(k + rank_i)
        其中 k=60（经典参数），rank_i 是文档在第 i 个检索器中的排名。

        【举例】
        某文档在向量检索排第 2，BM25 排第 5：
            RRF 分数 = 1/(60+2) + 1/(60+5) = 0.0161 + 0.0154 = 0.0315
        某文档在向量检索排第 1，BM25 排第 20：
            RRF 分数 = 1/(60+1) + 1/(60+20) = 0.0164 + 0.0125 = 0.0289
        前一个文档胜出，因为两个检索器都给了较高排名。

        【为什么要去重】
        两路检索可能返回相同的文档，按 text 内容去重，分数累加。
        """
        scores: dict[str, float] = {}   # text → RRF 累计分数
        doc_map: dict[str, dict] = {}   # text → 原始文档信息

        # 向量检索排名
        for rank, item in enumerate(vector_results):
            key = item.get("text", "")
            if key:
                scores[key] = scores.get(key, 0) + 1.0 / (k + rank + 1)
                doc_map[key] = item

        # BM25 检索排名
        for rank, item in enumerate(bm25_results):
            key = item.get("text", "")
            if key:
                scores[key] = scores.get(key, 0) + 1.0 / (k + rank + 1)
                if key not in doc_map:
                    doc_map[key] = item  # 只保存第一次出现的信息

        # 按 RRF 分数降序，截取 top_k
        sorted_keys = sorted(scores, key=scores.get, reverse=True)[:top_k]
        return [doc_map[key] for key in sorted_keys if key in doc_map]

    # =====================================================================
    # LLM 生成
    # =====================================================================

    def _generate(self, question: str, context_parts: List[str]) -> str:
        """
        基于检索到的上下文，让 LLM 生成答案。

        【Prompt 构成】
        SystemMessage（系统提示）= 告诉 LLM "你是谁" + 行为约束
          类似于 Java 中设定接口规范："你必须返回 JSON 格式"

        HumanMessage（用户消息）= 实际的问题 + 参考资料
          类似于 Java 中传入方法参数

        【为什么用 SystemMessage 而不是全塞一个 prompt 里】
        LLM 对 SystemMessage 的遵从度高于普通 User 消息。
        用 SystemMessage 设置角色和行为规范，效果更好。
        """
        # 系统提示：定义角色和行为
        system_prompt = (
            "你是一个专业的知识问答助手。请根据提供的参考资料回答问题。\n"
            "要求：\n"
            "1. 如果参考资料不足以回答问题，请如实说明。\n"
            "2. 回答应简洁、准确、有条理。\n"
            "3. 引用资料中的关键信息，但不要逐字复制大段内容。\n"
            "4. 使用中文回答。"
        )

        # 用分隔线清晰区分多个参考资料片段
        context_text = "\n\n---\n\n".join(context_parts)
        user_prompt = (
            f"参考资料：\n{context_text}\n\n"
            f"问题：{question}\n\n"
            f"请基于以上参考资料回答问题。"
        )

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        # 调用 LLM（invoke = 非流式，返回完整响应）
        response = self.llm.invoke(messages)
        return response.content if hasattr(response, "content") else str(response)

    def _generate_direct(self, question: str) -> str:
        """
        无参考资料时的直接回答（不依赖知识库）。

        当 Qdrant 检索为空或知识库没有相关文档时，
        让 LLM 凭自身知识回答问题。

        此时 confidence=0.0，前端可以提示"此答案基于通用知识，非私有知识库"。
        """
        messages = [
            SystemMessage(content="你是一个专业的知识问答助手。请简洁准确地回答用户的问题。使用中文。"),
            HumanMessage(content=question),
        ]
        response = self.llm.invoke(messages)
        return response.content if hasattr(response, "content") else str(response)

    # =====================================================================
    # 缓存管理
    # =====================================================================

    def clear_bm25_cache(self, kb_id: Optional[str] = None) -> None:
        """
        清除 BM25 缓存。

        何时调用：
        - 文档新增后：清除该 KB 的缓存，下次查询时重建
        - 文档删除后：同上
        - 不传 kb_id：清除所有缓存（如服务重启时）
        """
        if kb_id:
            self._bm25_cache.pop(kb_id, None)
        else:
            self._bm25_cache.clear()