"""
奖项 Schema 模块

定义奖项相关请求和响应数据结构的 Pydantic 模型。
采用 Base / Create / Update / Response 四层 Schema 模式。
"""

from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional

from schemas.enums import AwardLevel


class AwardBase(BaseModel):
    """
    奖项数据的基础 Schema

    包含创建和读取操作共享的通用字段。
    level 限制为 AwardLevel 枚举值。
    """

    title: str = Field(..., description="奖项名称")
    organization: str = Field(..., description="颁发机构")
    award_date: date = Field(..., description="获奖日期")
    level: AwardLevel = Field(..., description="奖项级别")


class AwardCreate(AwardBase):
    """
    创建新奖项的 Schema

    继承 AwardBase 的所有字段及校验规则。
    """
    pass


class AwardUpdate(BaseModel):
    """
    更新现有奖项的 Schema

    所有字段均为可选，允许部分更新（PATCH 语义）。
    """

    title: Optional[str] = None
    organization: Optional[str] = None
    award_date: Optional[date] = None
    level: Optional[AwardLevel] = None


class Award(AwardBase):
    """
    奖项响应 Schema

    在 AwardBase 基础上扩展只读字段：ID 和时间戳。
    """

    id: int = Field(..., description="奖项 ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    model_config = {"from_attributes": True}