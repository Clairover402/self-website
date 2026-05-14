"""
=============================================================================
RAG 核心模块 — Query 管线 (Query Pipeline)
=============================================================================

RAG 查询全流程：
Query 改写 → 向量化 → 混合检索(向量+BM25) → 合并去重 → 重排序 → Prompt 构建 → LLM 生成
"""

from typing import List, Optional
from dataclasses import dataclass, field
from collections import OrderedDict

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from .embedding import EmbeddingService
from .reranker import RerankerService
from .qdrant_store import QdrantStore
from .rewriter import QueryRewriter, RewrittenQuery
from core.config import settings


@dataclass
class QueryResult:
    answer: str
    sources: List[str] = field(default_factory=list)
    confidence: float = 0.0


class QueryPipeline:
    """RAG 查询管线"""

    def __init__(self):
        self.embedder = EmbeddingService()
        self.reranker = RerankerService()
        self.store = QdrantStore()
        self.rewriter = QueryRewriter()
        self._llm: ChatOpenAI | None = None
        self._bm25_cache: dict[str, tuple[list[str], object]] = {}

    @property
    def llm(self) -> ChatOpenAI:
        if self._llm is None:
            self._llm = ChatOpenAI(
                model="deepseek-chat",
                api_key=settings.DEEPSEEK_API_KEY,
                base_url=settings.DEEPSEEK_BASE_URL,
                temperature=0.3,
            )
        return self._llm

    def query(
        self,
        question: str,
        kb_id: Optional[str] = None,
        top_k: int | None = None,
    ) -> QueryResult:
        retrieval_k = top_k or settings.RETRIEVAL_TOP_K

        # =================================================================
        # Step 0: Query 改写（LLM 驱动，异常时回退到原始问题）
        # =================================================================
        rewritten = self.rewriter.rewrite(question)

        # =================================================================
        # Step 1: 对每条改写查询分别检索
        # =================================================================
        all_candidates: dict[str, dict] = {}  # text → candidate（去重）

        for search_query in rewritten.search_queries:
            try:
                query_vector = self.embedder.embed_query(search_query)
            except Exception:
                continue

            try:
                candidates = self._hybrid_retrieval(
                    kb_id=kb_id or "default",
                    query_text=search_query,
                    query_vector=query_vector,
                    top_k=retrieval_k,
                )
            except Exception:
                continue

            for c in candidates:
                text = c.get("text", "")
                if not text:
                    continue
                # 去重：保留更高分的条目
                if text not in all_candidates or c.get("score", 0) > all_candidates[text].get("score", 0):
                    all_candidates[text] = c

        merged = list(all_candidates.values())

        # 优雅降级：无检索结果时直接用 LLM 回答
        if not merged:
            answer = self._generate_direct(question)
            return QueryResult(answer=answer, sources=[], confidence=0.0)

        # =================================================================
        # Step 2: 重排序（使用原始问题，非改写后的查询）
        # =================================================================
        candidate_texts = [c["text"] for c in merged]
        rerank_k = settings.RERANK_TOP_K
        reranked = self.reranker.rerank(rewritten.original, candidate_texts, top_k=rerank_k)

        top_docs: list[tuple[str, float]] = []
        for idx, doc, score in reranked:
            top_docs.append((doc, score))

        if not top_docs:
            answer = self._generate_direct(question)
            return QueryResult(answer=answer, sources=[], confidence=0.0)

        # =================================================================
        # Step 3: LLM 生成（使用原始问题 + 检索到的上下文）
        # =================================================================
        context_parts = [doc for doc, _ in top_docs]
        sources = list(OrderedDict.fromkeys(
            c.get("doc_id", "") for c in merged
        ))
        confidence = top_docs[0][1] if top_docs else 0.0
        answer = self._generate(rewritten.original, context_parts)

        return QueryResult(
            answer=answer,
            sources=sources[:rerank_k],
            confidence=round(confidence, 4),
        )

    def _hybrid_retrieval(
        self,
        kb_id: str,
        query_text: str,
        query_vector: List[float],
        top_k: int,
    ) -> List[dict]:
        try:
            vector_results = self.store.search(kb_id, query_vector, top_k=top_k * 2)
        except Exception:
            vector_results = []

        try:
            bm25_results = self._bm25_search(kb_id, query_text, top_k=top_k * 2)
        except Exception:
            bm25_results = []

        if not bm25_results:
            return vector_results[:top_k] if vector_results else []

        if not vector_results:
            return bm25_results[:top_k]

        return self._rrf_fusion(vector_results, bm25_results, k=60, top_k=top_k)

    def _bm25_search(
        self,
        kb_id: str,
        query_text: str,
        top_k: int,
    ) -> List[dict]:
        try:
            from rank_bm25 import BM25Okapi
        except ImportError:
            return []

        if kb_id not in self._bm25_cache:
            self._rebuild_bm25_index(kb_id)

        all_chunks, bm25 = self._bm25_cache.get(kb_id, ([], None))
        if not all_chunks or bm25 is None:
            return []

        tokenized_query = query_text.split()
        scores = bm25.get_scores(tokenized_query)
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)

        return [
            {"text": all_chunks[i], "score": float(score), "doc_id": ""}
            for i, score in ranked[:top_k]
        ]

    def _rebuild_bm25_index(self, kb_id: str) -> None:
        try:
            from rank_bm25 import BM25Okapi
        except ImportError:
            return

        all_texts = self._get_all_chunk_texts(kb_id)
        if all_texts:
            tokenized = [text.split() for text in all_texts]
            self._bm25_cache[kb_id] = (all_texts, BM25Okapi(tokenized))

    def _get_all_chunk_texts(self, kb_id: str) -> List[str]:
        try:
            name = self.store.collection_name(kb_id)
            client = self.store.client
            if not client.collection_exists(name):
                return []

            texts: list[str] = []
            offset = None
            while True:
                records, next_offset = client.scroll(
                    collection_name=name,
                    limit=1000,
                    offset=offset,
                    with_payload=["text"],
                    with_vectors=False,
                )
                for record in records:
                    if record.payload and "text" in record.payload:
                        texts.append(record.payload["text"])
                if next_offset is None:
                    break
                offset = next_offset
            return texts
        except Exception:
            return []

    def _rrf_fusion(
        self,
        vector_results: List[dict],
        bm25_results: List[dict],
        k: int = 60,
        top_k: int = 10,
    ) -> List[dict]:
        scores: dict[str, float] = {}
        doc_map: dict[str, dict] = {}

        for rank, item in enumerate(vector_results):
            key = item.get("text", "")
            if key:
                scores[key] = scores.get(key, 0) + 1.0 / (k + rank + 1)
                doc_map[key] = item

        for rank, item in enumerate(bm25_results):
            key = item.get("text", "")
            if key:
                scores[key] = scores.get(key, 0) + 1.0 / (k + rank + 1)
                if key not in doc_map:
                    doc_map[key] = item

        sorted_keys = sorted(scores, key=scores.get, reverse=True)[:top_k]
        return [doc_map[key] for key in sorted_keys if key in doc_map]

    def _generate(self, question: str, context_parts: List[str]) -> str:
        system_prompt = (
            "你是一个专业的知识问答助手。请根据提供的参考资料回答问题。\n"
            "要求：\n"
            "1. 如果参考资料不足以回答问题，请如实说明。\n"
            "2. 回答应简洁、准确、有条理。\n"
            "3. 引用资料中的关键信息，但不要逐字复制大段内容。\n"
            "4. 使用中文回答。"
        )

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
        response = self.llm.invoke(messages)
        return response.content if hasattr(response, "content") else str(response)

    def _generate_direct(self, question: str) -> str:
        messages = [
            SystemMessage(content="你是一个专业的知识问答助手。请简洁准确地回答用户的问题。使用中文。"),
            HumanMessage(content=question),
        ]
        response = self.llm.invoke(messages)
        return response.content if hasattr(response, "content") else str(response)

    def clear_bm25_cache(self, kb_id: Optional[str] = None) -> None:
        if kb_id:
            self._bm25_cache.pop(kb_id, None)
        else:
            self._bm25_cache.clear()
