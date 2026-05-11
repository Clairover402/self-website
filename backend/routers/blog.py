"""
博客路由

定义博客管理操作的 REST API 端点。
处理博客文章的 CRUD 操作，包括创建、检索、更新和删除。

列表端点支持：分页（page/page_size）、搜索（search）、标签过滤（tag，枚举约束）。
"""

import math
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database.session import get_db
from schemas.blog import Blog, BlogCreate, BlogUpdate
from schemas.enums import BlogTag
from services.blog_service import BlogService
from utils.result import Result

router = APIRouter()
blog_service = BlogService()


@router.get("/", response_model=Result[dict])
async def get_blogs(
    # 分页参数：从查询字符串解析，带默认值和约束
    page: int = Query(default=1, ge=1, description="页码（从 1 开始）"),
    page_size: int = Query(default=10, ge=1, le=100, description="每页条数（1-100）"),
    # 搜索参数：在标题和摘要中模糊匹配
    search: Optional[str] = Query(default=None, description="搜索关键词"),
    # 标签过滤：使用 BlogTag 枚举约束，非法值会被 FastAPI 自动拒绝（返回 422）
    # Swagger UI 中自动展示为下拉菜单
    tag: Optional[BlogTag] = Query(default=None, description="按标签过滤"),
    db: Session = Depends(get_db),
):
    """
    获取博客文章列表（分页）

    支持组合过滤：可同时使用 search、tag 和分页参数。
    例如：GET /api/blogs?page=1&page_size=10&search=vue&tag=前端

    tag 参数受 BlogTag 枚举约束，Swagger UI 提供下拉选择。
    """
    # 将页码转换为数据库 offset
    offset = (page - 1) * page_size

    # BlogTag 继承 str，可直接当字符串传给 CRUD 层
    blogs, total = blog_service.get_all_blogs(
        db,
        offset=offset,
        limit=page_size,
        search=search,
        tag=tag.value if tag else None,
    )

    # 计算总页数，向上取整
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return Result.ok(data={
        "items": blogs,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    })


@router.get("/{slug}", response_model=Result[Blog])
async def get_blog(slug: str, db: Session = Depends(get_db)):
    """
    根据 slug 获取单篇博客详情

    每次访问自动增加浏览量计数。
    """
    blog = blog_service.get_blog_by_slug(slug, db)
    if not blog:
        return Result.fail(errorMsg="博客未找到", errCode="BLOG_NOT_FOUND")
    return Result.ok(data=blog)


@router.post("/", response_model=Result[Blog])
async def create_blog(blog: BlogCreate, db: Session = Depends(get_db)):
    """
    创建新博客文章

    请求体中的 tags 必须全部是 BlogTag 枚举值，否则 FastAPI 返回 422。
    枚举定义见 schemas/enums.py。
    """
    new_blog = blog_service.create_blog(blog, db)
    return Result.ok(data=new_blog)


@router.put("/{slug}", response_model=Result[Blog])
async def update_blog(slug: str, blog_update: BlogUpdate, db: Session = Depends(get_db)):
    """
    更新博客文章（部分更新）

    只更新请求体中传入的非 None 字段。
    tags 更新时同样受 BlogTag 枚举约束。
    """
    updated_blog = blog_service.update_blog(slug, blog_update, db)
    if not updated_blog:
        return Result.fail(errorMsg="博客未找到", errCode="BLOG_NOT_FOUND")
    return Result.ok(data=updated_blog)


@router.delete("/{slug}", response_model=Result[dict])
async def delete_blog(slug: str, db: Session = Depends(get_db)):
    """
    删除博客文章

    成功删除返回确认消息，文章不存在返回错误。
    """
    success = blog_service.delete_blog(slug, db)
    if not success:
        return Result.fail(errorMsg="博客未找到", errCode="BLOG_NOT_FOUND")
    return Result.ok(data={"message": "博客删除成功"})
