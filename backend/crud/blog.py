"""
博客 CRUD 操作模块

提供博客文章的数据库增删改查操作。
使用 SQLAlchemy 2.0 风格的 select() 语句替代已废弃的 session.query()。
所有方法接收 Session 实例作为依赖注入，便于测试时替换。

分页与过滤说明：
- 分页通过 offset/limit 实现，offset 从 0 开始计算
- 搜索使用 SQL LIKE 对标题和摘要做模糊匹配
- 标签过滤使用 MySQL JSON_CONTAINS 函数精确匹配标签列表中的值
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import select, func, cast, String
from sqlalchemy.orm import Session
from models.blog import BlogModel
from schemas.blog import BlogCreate, BlogUpdate


def get_all(
    db: Session,
    offset: int = 0,
    limit: int = 10,
    search: Optional[str] = None,
    tag: Optional[str] = None,
) -> list[BlogModel]:
    """
    获取博客文章列表（支持分页、搜索、标签过滤）

    参数：
        offset: SQL OFFSET 值（由调用方根据 page 计算）
        limit: 每页最大条数
        search: 模糊搜索关键词，同时匹配标题和摘要
        tag: 标签过滤，使用 JSON_CONTAINS 精确匹配

    所有过滤参数均为可选，不传时返回全部数据。
    """
    stmt = select(BlogModel)

    # 搜索过滤：在标题和摘要中进行 LIKE 模糊匹配
    if search:
        like_pattern = f"%{search}%"
        stmt = stmt.where(
            BlogModel.title.like(like_pattern) | BlogModel.excerpt.like(like_pattern)
        )

    # 标签过滤：将 JSON 数组转为字符串后检查是否包含 "tag" 精确匹配
    # 兼容 MySQL（JSON_CONTAINS）和 SQLite（无 JSON_CONTAINS）两种方言
    # 使用 cast + contains 实现跨数据库兼容
    if tag:
        stmt = stmt.where(
            cast(BlogModel.tags, String).contains(f'"{tag}"')
        )

    # 分页：先按创建时间倒序排列，再截取指定页
    stmt = stmt.order_by(BlogModel.created_at.desc()).offset(offset).limit(limit)
    return db.execute(stmt).scalars().all()


def count_all(
    db: Session,
    search: Optional[str] = None,
    tag: Optional[str] = None,
) -> int:
    """
    统计符合条件的博客总数

    与 get_all 使用完全相同的过滤条件，确保 total 值准确。
    使用 func.count() 替代获取全部数据后在 Python 中数长度，
    避免不必要的数据传输开销。
    """
    stmt = select(func.count(BlogModel.id))

    if search:
        like_pattern = f"%{search}%"
        stmt = stmt.where(
            BlogModel.title.like(like_pattern) | BlogModel.excerpt.like(like_pattern)
        )

    if tag:
        stmt = stmt.where(
            cast(BlogModel.tags, String).contains(f'"{tag}"')
        )

    return db.execute(stmt).scalar() or 0


def get_by_slug(db: Session, slug: str) -> Optional[BlogModel]:
    """
    根据 slug（URL 别名）查找单篇博客

    slug 是博客的唯一标识符，用于生成友好的 URL 路径。
    返回 None 表示未找到对应文章。
    """
    stmt = select(BlogModel).where(BlogModel.slug == slug)
    return db.execute(stmt).scalars().first()


def create(db: Session, blog_create: BlogCreate) -> BlogModel:
    """
    创建新博客文章

    从 Pydantic Schema（已通过路由层校验）构造 ORM 实例。
    tags 和 read_time 提供默认值，避免 NULL。
    创建后执行 commit + refresh 以确保数据库生成的主键和时间戳回填到实例。
    """
    blog = BlogModel(
        title=blog_create.title,
        slug=blog_create.slug,
        excerpt=blog_create.excerpt,
        content=blog_create.content,
        cover=blog_create.cover,
        tags=blog_create.tags or [],       # 无标签时默认空列表
        read_time=blog_create.read_time or 0,  # 未指定时默认 0 分钟
    )
    db.add(blog)
    db.commit()       # 写入数据库
    db.refresh(blog)  # 回填数据库生成的 id、created_at、updated_at 等字段
    return blog


def update(db: Session, slug: str, blog_update: BlogUpdate) -> Optional[BlogModel]:
    """
    更新现有博客文章

    使用 model_dump(exclude_unset=True) 只提取客户端实际发送的字段，
    实现真正的部分更新（PATCH 语义）。
    更新时自动刷新 updated_at 时间戳。
    返回 None 表示 slug 对应的文章不存在。
    """
    blog = get_by_slug(db, slug)
    if not blog:
        return None

    # exclude_unset=True：只取客户端显式传入的字段，未传的字段不出现在字典中
    update_data = blog_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(blog, key, value)

    # 手动刷新更新时间戳
    blog.updated_at = datetime.now()
    db.commit()
    db.refresh(blog)
    return blog


def delete(db: Session, slug: str) -> bool:
    """
    删除博客文章

    先查找再删除，返回 True 表示删除成功，False 表示文章不存在。
    不会抛出异常，由路由层根据返回值决定响应。
    """
    blog = get_by_slug(db, slug)
    if not blog:
        return False
    db.delete(blog)
    db.commit()
    return True
