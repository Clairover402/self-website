"""
=============================================================================
RAG 核心模块 — 嵌入服务 (Embedding Service)
=============================================================================

【RAG 概念入门】
RAG = Retrieval Augmented Generation = 检索增强生成
简单说：先把你的文档变成"数学坐标"（向量），提问时找到最相关的文档片段，
塞给大模型让它基于这些资料回答。

本模块做的是"变成数学坐标"这一步，叫做 Embedding（嵌入/向量化）。

【类比你熟悉的领域】
Embedding 就像 MySQL 的全文索引(Full-Text Index)：
- MySQL 全文索引用词频/逆文档频率(TF-IDF)做关键字匹配
- Embedding 把文字映射到高维空间中的坐标，用余弦距离衡量语义相似度
  比如 "苹果手机" 和 "iPhone" 在向量空间中会很近，即使字面完全不同

【BGE-M3 是什么】
BAAI（北京智源研究院）开源的嵌入模型。
"M3" = Multi-Lingual, Multi-Granularity, Multi-Functionality
- 支持多语言（中英文都很好）
- 支持多粒度（词级、句级、段落级都能处理）
- 输出 1024 维向量，每个维度是一个 float

【为何用单例模式】
嵌入模型加载到 GPU/内存需要几 GB 显存和数秒时间。
如果每次请求都新创建一个实例，内存会爆、速度会慢。
所以用单例：整个进程只加载一次，所有请求共享。
Java 中相当于：private static final EmbeddingService INSTANCE = new ...();
=============================================================================
"""

from typing import List
from collections import OrderedDict
from threading import Lock

# SentenceTransformer：HuggingFace 生态的嵌入模型统一接口
# 类比 Java 的 JDBC —— 不管底层是 MySQL 还是 PostgreSQL，操作方式都一样
from sentence_transformers import SentenceTransformer

# 项目全局配置，类似 Java 的 @Value 注入或 .properties 文件
from core.config import settings



class LRUCache:
    """
    线程安全的 LRU 缓存，基于 OrderedDict。
    用于缓存 embed_query() 结果。
    """

    def __init__(self, maxsize: int = 10000):
        self.maxsize = maxsize
        self.cache: OrderedDict[str, list] = OrderedDict()
        self.hits = 0
        self.misses = 0
        self._lock = Lock()

    def get(self, key: str):
        with self._lock:
            if key in self.cache:
                self.cache.move_to_end(key)
                self.hits += 1
                return self.cache[key]
            self.misses += 1
            return None

    def set(self, key: str, value):
        with self._lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            else:
                if len(self.cache) >= self.maxsize:
                    self.cache.popitem(last=False)
            self.cache[key] = value

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


class EmbeddingService:
    """
    BGE-M3 嵌入服务（单例 + 懒加载）

    【单例模式说明】
    Python 的 __new__ 类似 Java 的构造器，但更底层。
    这里重写 __new__ 确保整个进程只有一个 EmbeddingService 实例。
    等价于 Java 中：
        public static EmbeddingService getInstance() {
            if (instance == null) instance = new EmbeddingService();
            return instance;
        }

    【懒加载】
    模型只在实际第一次调用时才加载（不是 import 时立即加载）。
    这样服务启动快，只在真正需要用时才占用内存。
    """

    # 类变量（静态变量），存储唯一实例
    _instance: "EmbeddingService | None" = None
    # 类变量，存储已加载的模型对象
    _model: SentenceTransformer | None = None
    # LRU 缓存（类级别，所有实例共享）
    _lru_cache: LRUCache | None = None
    _lru_call_count: int = 0  # 用于定期输出命中率

    def __new__(cls) -> "EmbeddingService":
        """
        控制实例创建 —— 单例核心
        如果还没创建过实例，就创建一个；否则返回已有的。
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def model(self) -> SentenceTransformer:
        """
        获取嵌入模型（懒加载）

        @property 是 Python 的 getter 装饰器，相当于 Java 的 getModel() 方法。
        第一次访问时从磁盘/HuggingFace 加载模型到内存。
        后续访问直接返回已加载的模型，不再重复加载。
        """
        if self._model is None:
            # 这里真正加载模型，BGE-M3 约 2GB，首次调用需要几秒
            self._model = SentenceTransformer(settings.EMBEDDING_MODEL)
        return self._model

    @property
    def dim(self) -> int:
        """
        返回嵌入向量的维度
        BGE-M3 输出 1024 维向量，即 1024 个 float 组成的列表。
        这个值在创建 Qdrant Collection 时必须知道（相当于建表时指定字段类型）。
        """
        return self.model.get_sentence_embedding_dimension()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        批量文档向量化 —— Ingest 阶段使用

        【为什么叫"批量"】
        一个文档会被切分成多个 chunk（文本片段），比如一篇长文切成 50 个 chunk。
        如果逐个调用 embed，每次都要做 GPU 数据传输，效率低。
        批量处理：一次性把 50 个 chunk 送到 GPU，并行计算，速度快数倍。

        类比 Java/MySQL：相当于批量 INSERT 而非逐条 INSERT。

        【normalize_embeddings=True 的含义】
        把向量归一化到单位球面上（模长=1）。
        好处：余弦相似度计算退化为点积，检索速度快很多。
        就像 MySQL 中把 VARCHAR 转成 CHAR(32) 做等值比较 —— 更简单更快。

        Args:
            texts: 文档 chunk 列表，如 ["第一段内容", "第二段内容", ...]

        Returns:
            二维浮点数列表，如 [[0.12, -0.34, ...], [0.56, 0.78, ...]]
            外层维度 = chunk 数量，内层维度 = 1024 (BGE-M3 的输出维度)
        """
        if not texts:
            return []
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        # .tolist() 把 numpy 数组转成 Python 原生列表，便于 JSON 序列化
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        """
        查询向量化 —— Query 阶段使用

        把用户的提问转成向量，用于在 Qdrant 中搜最相关的 chunk。

        【和 embed_documents 的区别】
        BGE-M3 对查询和文档有不同的编码策略：
        - 文档编码：生成稠密向量（dense），捕捉丰富语义
        - 查询编码：可以加上指令前缀（如 "为这个句子生成表示以用于检索相关文章："）
        虽然这里为了简洁没加指令前缀，但 encode 方法内部已做了区分处理。

        Args:
            text: 用户提问，如 "什么是 RAG 技术？"

        Returns:
            1024 维向量列表，如 [0.12, -0.34, 0.56, ...]
        """
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()
