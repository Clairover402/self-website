"""
RAG 核心模块 — 重排序服务 (Reranker Service)

在 Query 阶段，向量检索引擎（Qdrant）会从海量 chunk 中返回 Top-K 个候选。
但向量检索是"粗排"——快但不精确。Reranker 做"精排"——对 Top-K 个候选逐个评估和问题的相关度，重新排序。

BGE-reranker-v2-m3：BAAI 出品，专门做"判断文档和问题的相关性"。
Cross-Encoder 方式：(query, document) 拼成一对让模型直接打分，比 Embedding 的余弦相似度更准。
"""

from typing import List, Tuple
from FlagEmbedding import FlagReranker

# Patch: transformers 5.x 移除了 prepare_for_model，手动补回
from transformers import PreTrainedTokenizerBase
if not hasattr(PreTrainedTokenizerBase, 'prepare_for_model'):
    def _prepare_for_model(self, ids, pair_ids=None, truncation=False, max_length=None, padding=False, return_tensors=None):
        # ids and pair_ids are already input_ids (lists of ints), not raw text
        input_ids = ids
        if pair_ids is not None:
            if truncation == 'only_second':
                max_d_len = (max_length or 512) - len(input_ids) - 2  # -2 for [CLS] and [SEP]
                pair_ids = pair_ids[:max(max_d_len, 0)]
            input_ids = input_ids + pair_ids
        if max_length and len(input_ids) > max_length:
            input_ids = input_ids[:max_length]
        return {'input_ids': input_ids, 'token_type_ids': [0] * len(input_ids), 'attention_mask': [1] * len(input_ids)}
    PreTrainedTokenizerBase.prepare_for_model = _prepare_for_model

from core.config import settings


class RerankerService:
    """BGE Reranker 重排序服务（单例 + 懒加载）"""

    _instance: "RerankerService | None" = None
    _reranker: FlagReranker | None = None

    def __new__(cls) -> "RerankerService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def reranker(self) -> FlagReranker:
        if self._reranker is None:
            self._reranker = FlagReranker(
                settings.RERANKER_MODEL,
                use_fp16=True,
            )
        return self._reranker

    def rerank(
        self,
        query: str,
        documents: List[str],
        top_k: int | None = None,
    ) -> List[Tuple[int, str, float]]:
        if not documents:
            return []

        top_k = top_k or settings.RERANK_TOP_K
        pairs = [[query, doc] for doc in documents]
        scores = self.reranker.compute_score(pairs, normalize=True)

        if isinstance(scores, float):
            scores = [scores]

        ranked = sorted(
            enumerate(zip(documents, scores)),
            key=lambda x: x[1][1],
            reverse=True,
        )

        return [
            (idx, doc, score)
            for idx, (doc, score) in ranked[:top_k]
        ]
