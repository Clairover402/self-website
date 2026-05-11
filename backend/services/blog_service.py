from typing import Optional, List
from sqlalchemy.orm import Session
from schemas.blog import Blog, BlogCreate, BlogUpdate
from crud import blog_crud


class BlogService:

    def get_all_blogs(self, db: Session) -> List[Blog]:
        models = blog_crud.get_all(db)
        return [Blog.model_validate(m) for m in models]

    def get_blog_by_slug(self, slug: str, db: Session) -> Optional[Blog]:
        model = blog_crud.get_by_slug(db, slug)
        if not model:
            return None
        model.views += 1
        db.commit()
        db.refresh(model)
        return Blog.model_validate(model)

    def create_blog(self, blog_create: BlogCreate, db: Session) -> Blog:
        model = blog_crud.create(db, blog_create)
        return Blog.model_validate(model)

    def update_blog(self, slug: str, blog_update: BlogUpdate, db: Session) -> Optional[Blog]:
        model = blog_crud.update(db, slug, blog_update)
        if not model:
            return None
        return Blog.model_validate(model)

    def delete_blog(self, slug: str, db: Session) -> bool:
        return blog_crud.delete(db, slug)
