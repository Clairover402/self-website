"""
博客路由

定义博客管理操作的 REST API 端点。
处理博客文章的 CRUD 操作，包括创建、检索、更新和删除。
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.session import get_db
from schemas.blog import Blog, BlogCreate, BlogUpdate
from services.blog_service import BlogService
from utils.result import Result

router = APIRouter()
blog_service = BlogService()


@router.get("/", response_model=Result[list[Blog]])
async def get_blogs(db: Session = Depends(get_db)):
    blogs = blog_service.get_all_blogs(db)
    return Result.ok(data=blogs, total=len(blogs))


@router.get("/{slug}", response_model=Result[Blog])
async def get_blog(slug: str, db: Session = Depends(get_db)):
    blog = blog_service.get_blog_by_slug(slug, db)
    if not blog:
        return Result.fail(errorMsg="博客未找到", errCode="BLOG_NOT_FOUND")
    return Result.ok(data=blog)


@router.post("/", response_model=Result[Blog])
async def create_blog(blog: BlogCreate, db: Session = Depends(get_db)):
    new_blog = blog_service.create_blog(blog, db)
    return Result.ok(data=new_blog)


@router.put("/{slug}", response_model=Result[Blog])
async def update_blog(slug: str, blog_update: BlogUpdate, db: Session = Depends(get_db)):
    updated_blog = blog_service.update_blog(slug, blog_update, db)
    if not updated_blog:
        return Result.fail(errorMsg="博客未找到", errCode="BLOG_NOT_FOUND")
    return Result.ok(data=updated_blog)


@router.delete("/{slug}", response_model=Result[dict])
async def delete_blog(slug: str, db: Session = Depends(get_db)):
    success = blog_service.delete_blog(slug, db)
    if not success:
        return Result.fail(errorMsg="博客未找到", errCode="BLOG_NOT_FOUND")
    return Result.ok(data={"message": "博客删除成功"})
