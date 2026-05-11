"""
项目 Schema 模块

定义项目相关请求和响应数据结构的 Pydantic 模型。
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class ProjectBase(BaseModel):
    """
    项目数据的基础 Schema。
    
    包含创建和读取操作共享的通用字段。
    """
    
    name: str = Field(..., description="项目名称")
    description: str = Field(..., description="项目描述")
    icon: Optional[str] = Field(None, description="项目图标")
    status: str = Field(..., description="项目状态")
    year: Optional[str] = Field(None, description="年份")
    full_description: Optional[str] = Field(None, description="详细描述")
    features: Optional[List[str]] = Field(default_factory=list, description="功能特性")
    techs: Optional[List[str]] = Field(default_factory=list, description="技术栈")
    demo_url: Optional[str] = Field(None, description="演示地址")
    repo_url: Optional[str] = Field(None, description="仓库地址")


class ProjectCreate(ProjectBase):
    """
    创建新项目的 Schema。
    
    继承 ProjectBase 的所有字段。
    """
    pass


class ProjectUpdate(BaseModel):
    """
    更新现有项目的 Schema。
    
    所有字段都是可选的，允许部分更新。
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
    响应中返回项目数据的 Schema。
    
    扩展 ProjectBase，添加 ID 和时间戳字段。
    """
    
    id: int = Field(..., description="项目 ID")
    created_at: datetime = Field(..., description="创建时间")

    model_config = {"from_attributes": True}