"""
统一响应结果 Schema 模块

定义 API 统一响应格式的 Pydantic 模型，
包含成功/失败状态、错误信息、响应数据和分页信息。
"""

from typing import TypeVar, Generic, Optional
from pydantic import BaseModel, Field

T = TypeVar('T')


class Result(BaseModel, Generic[T]):
    """
    统一 API 响应格式。

    提供标准化的响应结构，包含操作状态、错误信息、
    响应数据和分页信息。

    类型参数：
        T: 响应数据的类型

    示例：
        Result[int](success=True, data=42)
        Result[list](success=True, data=[], total=100)
        Result[dict](success=False, errorMsg="操作失败", errCode="E001")
    """

    success: bool = Field(default=True, description="操作是否成功")
    errorMsg: Optional[str] = Field(default=None, description="错误信息，成功时为 None")
    data: Optional[T] = Field(default=None, description="响应数据，类型为 T")
    total: Optional[int] = Field(default=None, description="数据总数，用于分页")
    errCode: Optional[str] = Field(default=None, description="错误码，用于程序化错误处理")

    model_config = {"from_attributes": True}

    @classmethod
    def ok(cls, data: T = None, total: Optional[int] = None) -> "Result[T]":
        """
        创建成功响应。

        参数：
            data: 响应数据
            total: 数据总数（可选，用于分页）

        返回：
            Result[T]: 成功响应实例
        """
        return cls(success=True, data=data, total=total, errorMsg=None, errCode=None)

    @classmethod
    def fail(cls, errorMsg: str, errCode: Optional[str] = None) -> "Result[None]":
        """
        创建失败响应。

        参数：
            errorMsg: 错误信息
            errCode: 错误码（可选）

        返回：
            Result[None]: 失败响应实例
        """
        return cls(success=False, errorMsg=errorMsg, errCode=errCode, data=None, total=None)
