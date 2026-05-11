from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from models.blog import BlogModel
from schemas.blog import BlogCreate, BlogUpdate


def get_all(db: Session) -> list[BlogModel]:
    return db.query(BlogModel).all()


def get_by_slug(db: Session, slug: str) -> Optional[BlogModel]:
    return db.query(BlogModel).filter(BlogModel.slug == slug).first()


def create(db: Session, blog_create: BlogCreate) -> BlogModel:
    blog = BlogModel(
        title=blog_create.title,
        slug=blog_create.slug,
        excerpt=blog_create.excerpt,
        content=blog_create.content,
        cover=blog_create.cover,
        tags=blog_create.tags or [],
        read_time=blog_create.read_time or 0,
    )
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return blog


def update(db: Session, slug: str, blog_update: BlogUpdate) -> Optional[BlogModel]:
    blog = get_by_slug(db, slug)
    if not blog:
        return None
    update_data = blog_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(blog, key, value)
    blog.updated_at = datetime.now()
    db.commit()
    db.refresh(blog)
    return blog


def delete(db: Session, slug: str) -> bool:
    blog = get_by_slug(db, slug)
    if not blog:
        return False
    db.delete(blog)
    db.commit()
    return True
