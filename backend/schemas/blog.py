"""
博客 Schema 模块

定义博客相关请求和响应数据结构的 Pydantic 模型。
采用 Base / Create / Update / Response 四层 Schema 模式。

tags 字段使用 BlogTag 枚举约束，确保标签值在预定义的 10 个范围内。
API 文档（Swagger UI）中会自动展示标签下拉选项。
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

from schemas.enums import BlogTag


class BlogBase(BaseModel):
    """
    博客数据的基础 Schema

    包含创建和读取操作共享的通用字段。
    tags 限制为 BlogTag 枚举值，非法标签会被 Pydantic 在校验阶段拒绝。
    """

    title: str = Field(..., description="博客标题")
    slug: str = Field(..., description="博客 URL 别名（唯一）")
    excerpt: str = Field(..., description="博客摘要")
    content: str = Field(..., description="博客内容（Markdown 格式）")
    cover: Optional[str] = Field(None, description="封面图 URL 或 emoji")

    # 标签列表：每个元素必须是 BlogTag 枚举成员
    # 默认空列表，创建时不传 tags 即为无标签文章
    tags: Optional[List[BlogTag]] = Field(
        default_factory=list,
        description=f"标签列表，可选值：{', '.join(BlogTag.all_values())}",
    )

    read_time: Optional[int] = Field(0, description="阅读时间（分钟）")


class BlogCreate(BlogBase):
    """
    创建新博客的 Schema

    继承 BlogBase 的所有字段及校验规则。
    前端/API 调用方只需传 BlogBase 定义的字段。
    """
    pass


class BlogUpdate(BaseModel):
    """
    更新现有博客的 Schema

    所有字段均为可选，允许部分更新（PATCH 语义）。
    tags 同样受 BlogTag 枚举约束，更新时传入的标签也必须合法。
    """

    title: Optional[str] = None
    slug: Optional[str] = None
    excerpt: Optional[str] = None
    content: Optional[str] = None
    cover: Optional[str] = None
    tags: Optional[List[BlogTag]] = None
    read_time: Optional[int] = None


class Blog(BlogBase):
    """
    博客响应 Schema

    在 BlogBase 基础上扩展只读字段：ID、浏览量、时间戳。
    通过 from_attributes=True 支持直接从 ORM 对象构造。
    """

    id: int = Field(..., description="博客 ID")
    views: int = Field(0, description="浏览次数")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    # 允许从 ORM 对象的属性直接构造 Pydantic 实例（Pydantic v2 替代旧版 orm_mode）
    model_config = {"from_attributes": True}
