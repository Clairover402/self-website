"""
=============================================================================
RAG 数据库模型 (SQLAlchemy ORM)
=============================================================================

【数据存储架构总览】
RAG 系统涉及两类存储：

  ① MySQL（关系型数据库）—— 存"元数据"
     - 知识库列表（名称、描述、是否默认）
     - 文档列表（文件名、类型、大小、状态）
     - 对话记录（问题、答案、来源、时间）

  ② Qdrant（向量数据库）—— 存"向量+文本"
     - Chunk 文本 + 1024维向量 + payload(文档ID等)

【为什么分两个库】
- MySQL 擅长：关系查询、事务、结构化数据
- Qdrant 擅长：向量相似度搜索、HNSW 索引
强行用 MySQL 存向量（如 pgvector 扩展）也可以，但性能差一个数量级。

【类比 Java 中的设计】
这里的 Model 类对应 Java 中的 JPA Entity / MyBatis 实体类：
    @Entity
    @Table(name = "knowledge_bases")
    public class KnowledgeBase {
        @Id @GeneratedValue
        private Long id;
        @Column(unique = true)
        private String kbId;
        ...
    }

Python 的 SQLAlchemy 采用声明式映射（Declarative Mapping），
不需要 XML 配置，类属性本身就是列定义。
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey

# Base 是所有 ORM 模型的共同基类
# 类比：JPA 中所有 @Entity 类共享同一个 PersistenceContext
from database.base import Base


class KnowledgeBaseModel(Base):
    """
    知识库元数据表 —— RAG 系统的"文件夹"。

    类比操作系统：一个知识库 = 一个文件夹
    用户可以创建多个知识库，分别上传不同主题的文档。

    表结构：
    ┌─────────────┬──────────┬──────────────────────────────┐
    │ 列名         │ 类型     │ 说明                         │
    ├─────────────┼──────────┼──────────────────────────────┤
    │ id           │ INT PK   │ 自增主键（内部使用）          │
    │ kb_id        │ VARCHAR  │ 对外 UUID（API 中使用）       │
    │ name         │ VARCHAR  │ 知识库名称（如"技术文档库"）  │
    │ description  │ TEXT     │ 描述（可选）                  │
    │ is_default   │ BOOL     │ 是否默认知识库                │
    │ created_at   │ DATETIME │ 创建时间                      │
    │ updated_at   │ DATETIME │ 更新时间（自动更新）          │
    └─────────────┴──────────┴──────────────────────────────┘

    【为什么有 id 和 kb_id 两个 ID】
    - id：数据库自增主键，内部关联用（外键引用高效，INT 比 VARCHAR 快）
    - kb_id：UUID 对外暴露，API 中用（防止遍历攻击，如 blog/1、blog/2...）
    类比 Java 中通常同时有数据库 ID 和业务 ID（如 orderId）。
    """
    __tablename__ = "knowledge_bases"  # 对应 MySQL 表名

    id = Column(Integer, primary_key=True, autoincrement=True)
    kb_id = Column(String(64), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)  # TEXT 类型无长度限制
    is_default = Column(Boolean, default=False)
    # default=datetime.now 是函数引用，每次 INSERT 时调用
    created_at = Column(DateTime, default=datetime.now)
    # onupdate=datetime.now 在每次 UPDATE 时自动更新
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class DocumentModel(Base):
    """
    文档元数据表 —— 记录上传的每个文档。

    注意：这里只存元数据（文件名、状态等），不存文件内容和向量。
    文件内容 → Qdrant（经过 Parser → Cleaner → Splitter → Embedding）
    元数据   → MySQL（本表）

    表结构：
    ┌───────────────────┬──────────┬─────────────────────────────┐
    │ 列名               │ 类型     │ 说明                        │
    ├───────────────────┼──────────┼─────────────────────────────┤
    │ id                 │ INT PK   │ 自增主键                     │
    │ doc_id             │ VARCHAR  │ 对外 UUID                    │
    │ knowledge_base_id  │ INT FK   │ 外键 → knowledge_bases.id    │
    │ filename           │ VARCHAR  │ 原始文件名                    │
    │ file_type          │ VARCHAR  │ MIME 类型                     │
    │ file_size          │ INT      │ 文件大小（字节）              │
    │ status             │ VARCHAR  │ 处理状态                     │
    │ chunk_count        │ INT      │ 切分出的 chunk 数量           │
    │ created_at         │ DATETIME │ 上传时间                      │
    └───────────────────┴──────────┴─────────────────────────────┘

    【status 枚举】
    - "processing"：正在摄入管线中处理
    - "completed"：成功完成，向量已写入 Qdrant
    - "failed"：处理失败（文件损坏、格式不支持等）
    """
    __tablename__ = "rag_documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(String(64), unique=True, nullable=False, index=True)
    # ForeignKey 创建外键约束，类似 MySQL 的 REFERENCES
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id"), nullable=False)
    filename = Column(String(500), nullable=False)
    file_type = Column(String(100), nullable=True)
    file_size = Column(Integer, default=0)
    status = Column(String(50), default="processing")
    chunk_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)


class RAGConversationModel(Base):
    """
    RAG 对话记录表 —— 记录每次问答。

    用于：
    - 展示对话历史
    - 分析用户提问模式
    - 评估 RAG 系统的回答质量

    【sources 字段】
    存 JSON 字符串，如 '["doc-uuid-1", "doc-uuid-2"]'
    前端可以据此展示"参考来源"。

    为什么不单独建来源表（多对多）？
    对个人网站规模来说，JSON 字段足够且更简单。
    如果以后需要按来源文档统计，可以迁移到关联表。
    """
    __tablename__ = "rag_conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String(64), unique=True, nullable=False, index=True)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id"), nullable=True)
    user_query = Column(Text, nullable=False)     # 用户问题
    answer = Column(Text, nullable=False)          # AI 回答
    sources = Column(Text, nullable=True)          # JSON 格式的来源文档 ID 列表
    created_at = Column(DateTime, default=datetime.now)