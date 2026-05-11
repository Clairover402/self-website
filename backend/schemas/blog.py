"""
博客 Schema 模块

定义博客相关请求和响应数据结构的 Pydantic 模型。
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class BlogBase(BaseModel):
    """
    博客数据的基础 Schema。
    
    包含创建和读取操作共享的通用字段。
    """
    
    title: str = Field(..., description="博客标题")
    slug: str = Field(..., description="博客 URL 别名")
    excerpt: str = Field(..., description="博客摘要")
    content: str = Field(..., description="博客内容（Markdown 格式）")
    cover: Optional[str] = Field(None, description="封面图标")
    tags: Optional[List[str]] = Field(default_factory=list, description="标签列表")
    read_time: Optional[int] = Field(0, description="阅读时间（分钟）")


class BlogCreate(BlogBase):
    """
    创建新博客的 Schema。
    
    继承 BlogBase 的所有字段。
    """
    pass


class BlogUpdate(BaseModel):
    """
    更新现有博客的 Schema。
    
    所有字段都是可选的，允许部分更新。
    """
    
    title: Optional[str] = None
    slug: Optional[str] = None
    excerpt: Optional[str] = None
    content: Optional[str] = None
    cover: Optional[str] = None
    tags: Optional[List[str]] = None
    read_time: Optional[int] = None


class Blog(BlogBase):
    """
    响应中返回博客数据的 Schema。
    
    扩展 BlogBase，添加 ID 和时间戳字段。
    """
    
    id: int = Field(..., description="博客 ID")
    views: int = Field(0, description="浏览次数")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    model_config = {"from_attributes": True}