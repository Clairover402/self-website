"""
=============================================================================
RAG 核心模块 — 重排序服务 (Reranker Service)
=============================================================================

【RAG 概念入门】
在 Query 阶段，向量检索引擎（Qdrant）会从海量 chunk 中返回 Top-K 个候选。
但向量检索是"粗排"——快但不精确。
Reranker 做"精排"——对 Top-K 个候选逐个评估和问题的相关度，重新排序。

【类比你熟悉的领域】
这就像 SQL 查询的两阶段过滤：
1. 第一阶段：用索引快速过滤（WHERE id IN (...)），类似向量检索的粗筛
2. 第二阶段：对结果集排序（ORDER BY relevance DESC LIMIT 5），类似 Reranker 的精排

MySQL 中：
    SELECT * FROM docs
    WHERE MATCH(content) AGAINST('关键词')   -- 粗筛
    ORDER BY custom_score(content, '关键词')  -- 精排
    LIMIT 5;

【BGE-reranker-v2-m3 是什么】
同样是 BAAI 出品，专门做"判断文档和问题的相关性"。
它不像 Embedding 那样各自编码再算距离，而是把 (query, document) 拼成一对，
让模型直接打分。这种方式更准，但也更慢（要对每一对做一次推理）。
所以策略是：先粗筛 10~20 个，再精排取 Top-5。

M3 = 基于 BGE-M3 的架构微调而来。
=============================================================================
"""

from typing import List, Tuple

# FlagEmbedding：BAAI 官方的嵌入/重排序工具包
# FlagReranker 封装了 cross-encoder 推理逻辑
from FlagEmbedding import FlagReranker

from core.config import settings


class RerankerService:
    """
    BGE Reranker 重排序服务（单例 + 懒加载）

    【Cross-Encoder vs Bi-Encoder】
    - Embedding(Bi-Encoder)：query 和 doc 各编各的，然后算相似度。
      快（可以预计算所有 doc 的向量），但精度较低（query 和 doc 没有交互）。
    - Reranker(Cross-Encoder)：query 和 doc 拼在一起喂给模型，
      让它们在同一层做 Attention。慢（每对都要推理），但精度高。

    类比：Bi-Encoder = 分别给两张照片打分再排序
         Cross-Encoder = 把两张照片放一起对比打分

    【use_fp16 的含义】
    FP16 = 半精度浮点数（16位），相对 FP32（32位）节省一半显存。
    对于推理任务，FP16 几乎不损失精度，但速度翻倍、显存减半。
    相当于 MySQL 中用 SMALLINT 代替 INT —— 数据范围够用就行，省空间。
    """

    _instance: "RerankerService | None" = None
    _reranker: FlagReranker | None = None

    def __new__(cls) -> "RerankerService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def reranker(self) -> FlagReranker:
        """懒加载重排序模型"""
        if self._reranker is None:
            self._reranker = FlagReranker(
                settings.RERANKER_MODEL,
                use_fp16=True,  # 半精度推理，省显存
            )
        return self._reranker

    def rerank(
        self,
        query: str,
        documents: List[str],
        top_k: int | None = None,
    ) -> List[Tuple[int, str, float]]:
        """
        对候选文档做精排，返回 Top-K 个最相关的。

        【工作流程】
        1. 构建 (query, doc) 配对列表
        2. 逐对打分（模型推理）
        3. 按分数降序排列
        4. 截取 top_k 个

        类比 SQL：
            SELECT *, SCORE(query, content) as relevance
            FROM candidates
            ORDER BY relevance DESC
            LIMIT {top_k}

        Args:
            query:   用户提问
            documents: 候选文档内容列表（已从 Qdrant 粗筛出来的）
            top_k:   最终保留几个（默认从配置取，通常 5）

        Returns:
            [(原始索引, 文档内容, 相关度分数), ...]
            原始索引指在 documents 列表中的位置，用于反向追踪来源。
            分数范围 [0, 1]，1 表示完全相关。

        【返回值设计说明】
        保留原始索引(index)很重要：
        后续需要通过索引找到原始文档的元数据（文件名、来源等）展示给用户。
        如果只返回排序后的文本，就丢失了溯源信息。
        """
        if not documents:
            return []

        top_k = top_k or settings.RERANK_TOP_K

        # 构建 (query, document) 配对
        # 比如 query="什么是RAG"，documents=["RAG是..."， "今天天气..."]
        # 变成 [("什么是RAG", "RAG是..."), ("什么是RAG", "今天天气...")]
        pairs = [[query, doc] for doc in documents]

        # 逐对打分（这一步最耗时，每个 pair 做一次模型推理）
        # normalize=True: 将分数归一化到 [0,1] 区间
        scores = self.reranker.compute_score(pairs, normalize=True)

        # 处理单文档的边界情况
        if isinstance(scores, float):
            scores = [scores]

        # 排序：按分数降序
        # enumerate 给每个元素加上序号，类似 Java 中 for (int i = 0; i < list.size(); i++)
        ranked = sorted(
            enumerate(zip(documents, scores)),
            key=lambda x: x[1][1],   # 取分数作为排序键
            reverse=True,             # 降序
        )

        # 截取 top_k 个，返回 (原始索引, 文档内容, 分数)
        return [
            (idx, doc, score)
            for idx, (doc, score) in ranked[:top_k]
        ]