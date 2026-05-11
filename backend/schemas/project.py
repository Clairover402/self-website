"""
项目 Schema 模块

定义项目相关请求和响应数据结构的 Pydantic 模型。
采用 Base / Create / Update / Response 四层 Schema 模式，
确保前端只看到应暴露的字段，避免过度暴露数据库实现细节。
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class ProjectBase(BaseModel):
    """
    项目数据的基础 Schema

    包含创建和读取操作共享的通用字段。
    所有字段均有中文 description，方便 API 文档自动生成。
    """

    name: str = Field(..., description="项目名称")
    description: str = Field(..., description="项目简短描述")
    icon: Optional[str] = Field(None, description="项目图标（emoji 或图标名）")
    status: str = Field(..., description="项目状态（如：进行中 / 已完成 / 维护中）")
    year: Optional[str] = Field(None, description="项目年份")
    full_description: Optional[str] = Field(None, description="项目完整描述（详情页展示）")
    features: Optional[List[str]] = Field(default_factory=list, description="功能特性列表")
    techs: Optional[List[str]] = Field(default_factory=list, description="技术栈列表")
    demo_url: Optional[str] = Field(None, description="演示地址")
    repo_url: Optional[str] = Field(None, description="仓库地址")


class ProjectCreate(ProjectBase):
    """
    创建新项目的 Schema

    继承 ProjectBase 的所有字段，无需额外字段。
    status 默认值由数据库层处理。
    """
    pass


class ProjectUpdate(BaseModel):
    """
    更新现有项目的 Schema

    所有字段均为可选，允许部分更新（PATCH 语义）。
    使用 exclude_unset=True 可只发送实际变更的字段。
    """

    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    status: Optional[str] = None
    year: Optional[str] = None
    full_description: Optional[str] = None
    features: Optional[List[str]] = None
    techs: Optional[List[str]] = None
    demo_url: Optional[str] = None
    repo_url: Optional[str] = None


class Project(ProjectBase):
    """
    项目响应 Schema

    在 ProjectBase 基础上扩展只读字段：ID 和时间戳。
    通过 from_attributes=True 支持直接从 ORM 对象构造。
    """

    id: int = Field(..., description="项目 ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    # 允许从 ORM 对象的属性直接构造 Pydantic 实例（替代旧版 orm_mode）
    model_config = {"from_attributes": True}
