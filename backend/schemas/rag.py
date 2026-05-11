"""
RAG Schema 模块

定义 RAG 相关请求和响应数据结构的 Pydantic 模型。
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict


class RAGQueryRequest(BaseModel):
    """
    RAG 查询请求的 Schema。
    
    包含用户的问题和可选的知识库 ID。
    """
    
    question: str = Field(..., description="用户问题")
    knowledge_base_id: Optional[str] = Field(None, description="知识库 ID")


class RAGQueryResponse(BaseModel):
    """
    RAG 查询响应的 Schema。
    
    包含 AI 生成的答案、来源和置信度分数。
    """
    
    answer: str = Field(..., description="AI 回答")
    sources: List[str] = Field(default_factory=list, description="引用来源")
    confidence: float = Field(0.0, description="置信度")


class KnowledgeBase(BaseModel):
    """
    知识库数据的 Schema。
    
    表示用于 RAG 操作的文档集合。
    """
    
    id: str = Field(..., description="知识库 ID")
    name: str = Field(..., description="知识库名称")
    description: Optional[str] = Field(None, description="知识库描述")
    is_default: bool = Field(False, description="是否为默认知识库")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    model_config = {"from_attributes": True}


class KnowledgeBaseCreate(BaseModel):
    """
    创建新知识库的 Schema。
    """
    
    name: str = Field(..., description="知识库名称")
    description: Optional[str] = Field(None, description="知识库描述")
    is_default: Optional[bool] = Field(False, description="是否设为默认")


class KnowledgeBaseUpdate(BaseModel):
    """
    更新现有知识库的 Schema。
    
    所有字段都是可选的，允许部分更新。
    """
    
    name: Optional[str] = None
    description: Optional[str] = None
    is_default: Optional[bool] = None


class Document(BaseModel):
    """
    文档数据的 Schema。
    
    表示上传到知识库的文件。
    """
    
    id: str = Field(..., description="文档 ID")
    knowledge_base_id: str = Field(..., description="所属知识库 ID")
    filename: str = Field(..., description="文件名")
    file_type: str = Field(..., description="文件类型")
    file_size: Optional[int] = Field(None, description="文件大小")
    status: str = Field("processing", description="处理状态")
    chunk_count: int = Field(0, description="分块数量")
    created_at: datetime = Field(..., description="上传时间")

    model_config = {"from_attributes": True}


class DocumentUploadResponse(BaseModel):
    """
    文档上传响应的 Schema。
    """
    
    message: str = Field(..., description="上传结果消息")
    document_id: Optional[str] = Field(None, description="上传的文档 ID")


class DocumentChunk(BaseModel):
    """
    文档分块数据的 Schema。
    
    表示为向量嵌入处理的文档片段。
    """
    
    id: str = Field(..., description="分块 ID")
    document_id: str = Field(..., description="所属文档 ID")
    chunk_index: int = Field(..., description="分块索引")
    content: str = Field(..., description="分块内容")
    embedding: Optional[str] = Field(None, description="向量嵌入")
    token_count: Optional[int] = Field(None, description="token 数量")
    metadata: Optional[Dict] = Field(None, description="元数据")


class RAGConversation(BaseModel):
    """
    RAG 对话数据的 Schema。
    
    表示与 AI 的单次交互。
    """
    
    id: str = Field(..., description="对话 ID")
    knowledge_base_id: Optional[str] = Field(None, description="知识库 ID")
    user_query: str = Field(..., description="用户查询")
    answer: str = Field(..., description="AI 回答")
    sources: List[str] = Field(default_factory=list, description="引用来源")
    created_at: datetime = Field(..., description="创建时间")

    model_config = {"from_attributes": True}