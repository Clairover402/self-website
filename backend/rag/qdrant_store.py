"""
=============================================================================
RAG 核心模块 — Qdrant 向量存储 (Qdrant Store)
=============================================================================

【RAG 概念入门】
文档被切分成 chunks、转成向量后，需要一个"向量数据库"来存储和检索。
Qdrant 就是专门做这件事的。

【类比你熟悉的 MySQL】
传统数据库和向量数据库的对应关系：

    MySQL                            Qdrant
    ─────                            ──────
    Database                         （无此概念，一个 Qdrant 实例即一个 DB）
    Table                            Collection
    Row                               Point
    Primary Key (INT)                 Point ID (UUID string)
    Column (VARCHAR, INT...)          Payload (JSON 格式的附加数据)
    B-Tree Index                      HNSW Index（向量索引）
    SELECT ... WHERE id = 1           retrieve(point_id)
    SELECT ... ORDER BY score         search(query_vector, limit=top_k)
    INSERT INTO table VALUES (...)    upsert(collection, points)
    DELETE FROM table WHERE ...       delete(collection, filter)
    DROP TABLE                        delete_collection(collection)

关键差异：
- MySQL 用 B-Tree 索引做等值/范围查找
- Qdrant 用 HNSW（Hierarchical Navigable Small World）近似最近邻搜索
  在百万级向量中找最相似的 Top-K 个，毫秒级完成

【HNSW 是什么】
一种图索引算法。想象在纸上散布很多点，HNSW 会在相近的点之间连线，
搜索时沿着线"跳跃"，快速逼近目标区域。
类比：快递员送快递时不逐家检查，而是先找到街区再找门牌号。

【每个知识库 = 一个 Collection】
Qdrant 中的 Collection 对应 MySQL 的表。
我们为每个知识库创建一个 Collection，命名为 kb_{kb_id}。
这样可以物理隔离不同知识库的数据，删除知识库时直接 drop collection 即可。
"""

from typing import List
from uuid import uuid4  # 生成全局唯一 ID

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,        # 距离度量方式：COSINE（余弦）、EUCLID（欧几里得）、DOT（点积）
    VectorParams,    # 向量参数：维度大小 + 距离度量
    PointStruct,     # 一个 Point 的数据结构：ID + 向量 + Payload
    Filter,          # 过滤条件
    FieldCondition,  # 字段条件
    MatchValue,      # 精确值匹配
)

from core.config import settings


class QdrantStore:
    """
    Qdrant 向量存储管理器（单例）。

    【架构职责】
    - 管理 Qdrant 连接（TCP 连接池复用）
    - 创建/删除 Collection（建表/删表）
    - 向量 CRUD 操作（增删查）

    【为什么是单例】
    连接池应该全局共享，避免每个请求都新建 TCP 连接。
    这就像 MySQL 的 DataSource 连接池——全局一个实例，所有 DAO 共享。
    """

    _instance: "QdrantStore | None" = None
    _client: QdrantClient | None = None

    def __new__(cls) -> "QdrantStore":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def client(self) -> QdrantClient:
        """
        获取 Qdrant 客户端（懒连接）。

        QdrantClient 内部维护 HTTP 连接池，类似 MySQL 的 ConnectionPool。
        首次调用时建立连接，后续复用。

        【配置说明】
        - url: Qdrant 服务的 HTTP 地址，Docker 部署时通常是 http://localhost:6333
        - api_key: Qdrant Cloud 需要，本地部署留空
        """
        if self._client is None:
            kwargs = {"url": settings.QDRANT_URL}
            if settings.QDRANT_API_KEY:
                kwargs["api_key"] = settings.QDRANT_API_KEY
            self._client = QdrantClient(**kwargs)
        return self._client

    # =========================================================================
    # Collection 管理
    # =========================================================================

    def collection_name(self, kb_id: str) -> str:
        """
        知识库 ID → Qdrant Collection 名称的映射规则。

        命名规则：kb_{kb_id}
        例如知识库 ID = "abc123" → Collection 名 = "kb_abc123"

        【为什么加 kb_ 前缀】
        1. 命名空间隔离：避免和未来可能的其他 Collection 冲突
        2. 可读性：一眼能看出这是知识库 Collection
        3. 安全：防止 kb_id 为纯数字时可能的歧义
        """
        return f"kb_{kb_id}"

    def ensure_collection(self, kb_id: str, vector_size: int) -> None:
        """
        确保 Collection 存在（不存在则创建）。

        类比 MySQL：
            CREATE TABLE IF NOT EXISTS kb_abc123 (
                id VARCHAR(64) PRIMARY KEY,
                vector FLOAT[1024],
                payload JSON,
                INDEX hnsw (vector) WITH (m=16, ef_construction=100)
            );

        【Distance.COSINE 的含义】
        用余弦相似度衡量向量之间的"远近"：
        - 1.0 = 方向完全相同（最相似）
        - 0.0 = 正交/不相关
        - -1.0 = 方向完全相反

        【hnsw_config=None】
        使用 Qdrant 默认的 HNSW 参数（m=16, ef_construct=100）。
        对个人网站规模完全够用，不需要手动调参。
        """
        name = self.collection_name(kb_id)
        if not self.client.collection_exists(name):
            self.client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(
                    size=vector_size,         # BGE-M3 = 1024
                    distance=Distance.COSINE,  # 余弦距离
                ),
                hnsw_config=None,  # 默认 HNSW 配置
            )

    def delete_collection(self, kb_id: str) -> None:
        """
        删除整个知识库的 Collection（DROP TABLE）。

        注意：这是不可逆操作，所有向量数据永久丢失。
        调用前 Service 层已确认用户意图。
        """
        name = self.collection_name(kb_id)
        if self.client.collection_exists(name):
            self.client.delete_collection(name)

    def collection_exists(self, kb_id: str) -> bool:
        """检查 Qdrant 中该 KB 的 Collection 是否存在。"""
        return self.client.collection_exists(self.collection_name(kb_id))

    def collection_count(self, kb_id: str) -> int:
        """
        获取 Collection 中的向量数量（SELECT COUNT(*)）。

        用于管理后台展示知识库的规模。
        """
        name = self.collection_name(kb_id)
        if not self.client.collection_exists(name):
            return 0
        info = self.client.get_collection(name)
        return info.points_count or 0

    # =========================================================================
    # 向量 CRUD
    # =========================================================================

    def upsert_chunks(
        self,
        kb_id: str,
        chunks: list[dict],
    ) -> List[str]:
        """
        批量写入/更新 chunks（INSERT ... ON DUPLICATE KEY UPDATE）。

        【为什么叫 upsert 而非 insert】
        Qdrant 的 upsert 语义：如果 Point ID 已存在则更新，否则插入。
        我们用 UUID 作为 Point ID，保证每次都是新插入（不会碰撞）。

        【数据流】
        chunk = {
            "text": "这是第一段内容...",      # 原始文本
            "embedding": [0.12, -0.34, ...],  # BGE-M3 生成的 1024 维向量
            "doc_id": "doc-uuid-123",          # 所属文档 ID（用于追溯和批量删除）
            "chunk_index": 0,                  # 在文档中的序号
        }

        【Payload 是什么】
        Payload 是附加到每个 Point 上的 JSON 数据，类似 MySQL 行中除主键和向
        量外的其他列。我们用它存储原始文本、文档 ID 等，便于检索时返回。

        Returns:
            写入的所有 chunk_id（UUID 字符串列表），用于日志/追踪
        """
        points: list[PointStruct] = []
        chunk_ids: list[str] = []

        for chunk in chunks:
            # 为每个 chunk 生成唯一 ID（类似 MySQL 自增主键，但用 UUID）
            chunk_id = str(uuid4())
            chunk_ids.append(chunk_id)

            # Payload：向量之外的所有数据
            payload = {
                "text": chunk["text"],
                "doc_id": chunk.get("doc_id", ""),
                "kb_id": kb_id,
                "chunk_index": chunk.get("chunk_index", 0),
            }

            points.append(PointStruct(
                id=chunk_id,         # 主键
                vector=chunk["embedding"],  # 向量
                payload=payload,     # 附加 JSON
            ))

        # 批量写入（一次网络请求完成所有写入）
        self.client.upsert(
            collection_name=self.collection_name(kb_id),
            points=points,
        )
        return chunk_ids

    def search(
        self,
        kb_id: str,
        query_vector: List[float],
        top_k: int | None = None,
    ) -> List[dict]:
        """
        向量相似度检索 —— RAG 的核心查询操作。

        类比 SQL：
            SELECT id, payload->>'text' as text, payload->>'doc_id' as doc_id,
                   COSINE_SIMILARITY(vector, :query_vector) as score
            FROM kb_abc123
            ORDER BY score DESC
            LIMIT :top_k;

        【工作原理】
        1. 用 HNSW 索引在百万级向量中快速找到最近的 top_k 个
        2. 返回 Point ID + 文本 + 文档 ID + 相似度分数
        3. 每次搜索耗时：通常 < 10ms（取决于数据量和 top_k）

        Args:
            kb_id:        知识库 ID
            query_vector: 问题的向量（1024 维 float 列表）
            top_k:        返回几条结果

        Returns:
            搜索结果列表，每项包含：id, text, doc_id, chunk_index, score
        """
        top_k = top_k or settings.RETRIEVAL_TOP_K

        results = self.client.query_points(
            collection_name=self.collection_name(kb_id),
            query=query_vector,
            limit=top_k,
            with_payload=True,
        )

        # 格式化返回结果
        return [
            {
                "id": hit.id,                              # Point 的 UUID
                "text": hit.payload.get("text", ""),       # 原始文本
                "doc_id": hit.payload.get("doc_id", ""),   # 所属文档 ID
                "chunk_index": hit.payload.get("chunk_index", 0),
                "score": hit.score,                         # 相似度分数
            }
            for hit in results.points
        ]

    def delete_by_doc_id(self, kb_id: str, doc_id: str) -> None:
        """
        按文档 ID 删除所有相关 chunks。

        类比 SQL：
            DELETE FROM kb_abc123 WHERE payload->>'doc_id' = :doc_id;

        Qdrant 使用 Filter + FieldCondition 实现条件删除，
        类似于 MySQL 的 WHERE 子句。

        【使用场景】
        用户删除某个已上传的文档时，需要同时删除该文档在 Qdrant 中
        的所有 chunk（一个文档可能被切分成几十个 chunk）。
        """
        self.client.delete(
            collection_name=self.collection_name(kb_id),
            points_selector=Filter(
                must=[  # must = AND 逻辑，should = OR 逻辑
                    FieldCondition(
                        key="doc_id",                  # 匹配 payload 中的字段
                        match=MatchValue(value=doc_id),  # 精确匹配
                    )
                ]
            ),
        )
