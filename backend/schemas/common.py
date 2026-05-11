"""
公共 Schema 模块

定义跨模块共享的通用 Pydantic 模型，包括分页参数和分页响应。
所有需要列表分页的路由统一使用此模块的类型，确保 API 一致性。
"""

from typing import TypeVar, Generic, Optional
from pydantic import BaseModel, Field

# 泛型类型变量，用于 PaginatedResult 的数据字段
T = TypeVar("T")


class PaginationParams(BaseModel):
    """
    分页请求参数

    用于 FastAPI 路由的 Depends() 注入，自动从查询字符串解析。
    例如：GET /api/blogs?page=2&page_size=20

    page 从 1 开始计数（非零基），符合常见 API 习惯。
    page_size 上限 100，防止单次查询拖垮数据库。
    """

    page: int = Field(
        default=1,
        ge=1,                              # 页码最小为 1
        description="页码（从 1 开始）"
    )
    page_size: int = Field(
        default=10,
        ge=1,                              # 每页至少 1 条
        le=100,                            # 每页最多 100 条，防止滥用
        description="每页条数（1-100）"
    )

    @property
    def offset(self) -> int:
        """
        计算 SQL OFFSET 值

        将页码转换为数据库查询用的偏移量。
        例如：page=1, page_size=10 → offset=0
              page=3, page_size=10 → offset=20
        """
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """直接返回 LIMIT 值，语义比 page_size 更清晰"""
        return self.page_size


class PaginatedResult(BaseModel, Generic[T]):
    """
    分页响应模型

    泛型类，T 为列表元素类型。
    包含当前页数据、分页元信息，方便前端渲染分页控件。

    使用示例：
        PaginatedResult[Blog](items=blogs, total=42, page=2, page_size=10)
    """

    items: list[T] = Field(..., description="当前页数据列表")
    total: int = Field(..., description="符合条件的数据总数（非当前页条数）")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页条数")
    total_pages: int = Field(..., description="总页数")
