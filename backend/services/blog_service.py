"""
博客服务模块

博客管理的业务逻辑层，位于 Router 和 CRUD 之间。
职责：
- 协调 CRUD 操作调用
- 处理业务规则（如浏览量自增）
- ORM 模型 → Pydantic Schema 转换

不直接操作数据库，所有数据访问委托给 crud 层。
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from schemas.blog import Blog, BlogCreate, BlogUpdate
from crud import blog_crud


class BlogService:
    """博客业务服务（无状态，方法接收 db session 作为参数）"""

    def get_all_blogs(
        self,
        db: Session,
        offset: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> tuple[List[Blog], int]:
        """
        获取博客列表（分页 + 搜索 + 过滤）

        返回：(博客列表, 符合条件的总数)
        列表为 Pydantic Schema 而不是 ORM 模型，防止数据库对象泄漏到路由层。
        """
        models = blog_crud.get_all(
            db, offset=offset, limit=limit, search=search, tag=tag
        )
        total = blog_crud.count_all(db, search=search, tag=tag)
        return [Blog.model_validate(m) for m in models], total

    def get_blog_by_slug(self, slug: str, db: Session) -> Optional[Blog]:
        """
        根据 slug 获取单篇博客详情

        每次访问自动将浏览量 +1（业务规则：阅读即计入浏览）。
        返回 None 表示文章不存在。
        """
        model = blog_crud.get_by_slug(db, slug)
        if not model:
            return None
        # 浏览量自增：每次读取都视为一次浏览
        model.views += 1
        db.commit()
        db.refresh(model)
        return Blog.model_validate(model)

    def create_blog(self, blog_create: BlogCreate, db: Session) -> Blog:
        """
        创建新博客

        Schema 校验已在路由层通过 Pydantic 完成，此处直接委托 CRUD。
        """
        model = blog_crud.create(db, blog_create)
        return Blog.model_validate(model)

    def update_blog(self, slug: str, blog_update: BlogUpdate, db: Session) -> Optional[Blog]:
        """
        更新博客

        支持部分更新：只更新传入的非 None 字段。
        """
        model = blog_crud.update(db, slug, blog_update)
        if not model:
            return None
        return Blog.model_validate(model)

    def delete_blog(self, slug: str, db: Session) -> bool:
        """删除博客，返回是否成功"""
        return blog_crud.delete(db, slug)
