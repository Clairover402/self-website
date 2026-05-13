"""
=============================================================================
应用全局配置 (Settings)
=============================================================================

【Pydantic Settings 原理】
Pydantic Settings 自动从 .env 文件读取环境变量并做类型转换。
类比 Spring Boot 的 @ConfigurationProperties + application.properties：
    @Value("${deepseek.api-key}")
    private String deepseekApiKey;

Python 版本更简洁：直接在类属性上声明类型，自动注入。
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    全局配置类。

    所有配置项都可以在 .env 文件中覆盖（环境变量优先级高于默认值）。
    """

    # ==================== 基础配置 ====================
    APP_NAME: str = "RAG 个人网站 API"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = True
    DATABASE_URL: str = "mysql+pymysql://root:123456@localhost:3306/self_website"

    # ==================== RAG — 大语言模型 ====================

    # DeepSeek API 密钥（从 https://platform.deepseek.com 获取）
    # 这是唯一必须用户自行配置的值
    DEEPSEEK_API_KEY: str = ""

    # DeepSeek API 地址（兼容 OpenAI SDK）
    # 默认使用官方 API，也可以换成代理地址
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"

    # ==================== RAG — 向量数据库 ====================

    # Qdrant 服务地址
    # Docker 本地部署：http://localhost:6333
    # Qdrant Cloud：https://xxx.cloud.qdrant.io
    QDRANT_URL: str = "http://localhost:6333"

    # Qdrant API 密钥（本地部署不需要，Cloud 需要）
    QDRANT_API_KEY: str = ""

    # ==================== RAG — 嵌入模型 ====================

    # BGE-M3 嵌入模型名称
    # 首次运行时自动从 HuggingFace 下载（约 2GB）
    # 模型在后台常驻内存，所有请求共享
    EMBEDDING_MODEL: str = "BAAI/bge-m3"

    # BGE Reranker 重排序模型名称
    # 同样是 BAAI 出品，专门做精排
    RERANKER_MODEL: str = "BAAI/bge-reranker-v2-m3"

    # ==================== RAG — 切分参数 ====================

    # Chunk 大小（字符数，非 token）
    # 500 字符 ≈ 750 token（中文每个字约 1.5 token）
    # 太小：语义不完整；太大：检索精度下降
    # 这是经过大量实验的经验值，可以后续用 RAGAS 调优
    CHUNK_SIZE: int = 500

    # Chunk 重叠量（相邻 chunk 重叠的字符数）
    # 50 字符 ≈ Chunk 大小的 10%，是常见的推荐比例
    CHUNK_OVERLAP: int = 50

    # ==================== RAG — 检索参数 ====================

    # 向量检索返回的候选数量（粗排阶段）
    # 10 是平衡速度和精度的经验值
    # 实际会取 20（top_k * 2）做 RRF 融合
    RETRIEVAL_TOP_K: int = 10

    # Reranker 重排序后保留的数量（精排阶段）
    # 从 10 个候选中选出最相关的 5 个塞给 LLM
    # 5 个 chunk ≈ 2500 字 ≈ 3750 token，在 LLM 窗口内很安全
    RERANK_TOP_K: int = 5

    # ==================== 配置元信息 ====================

    # 告诉 Pydantic 从 .env 文件加载配置
    model_config = SettingsConfigDict(env_file=".env")


# 全局单例（模块级变量）
# 类比：@Component + @Autowired 的全局 Bean
settings = Settings()