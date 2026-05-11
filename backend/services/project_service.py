"""
项目服务模块

作品集项目管理的业务逻辑层，位于 Router 和 CRUD 之间。
职责：
- 协调 CRUD 操作调用
- ORM 模型 → Pydantic Schema 转换

不直接操作数据库，所有数据访问委托给 crud 层。
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from schemas.project import Project, ProjectCreate, ProjectUpdate
from crud import project_crud


class ProjectService:
    """项目业务服务（无状态，方法接收 db session 作为参数）"""

    def get_all_projects(
        self,
        db: Session,
        offset: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        status: Optional[str] = None,
        tech: Optional[str] = None,
    ) -> tuple[List[Project], int]:
        """
        获取项目列表（分页 + 搜索 + 过滤）

        返回：(项目列表, 符合条件的总数)
        列表为 Pydantic Schema 而非 ORM 模型。
        """
        models = project_crud.get_all(
            db, offset=offset, limit=limit, search=search, status=status, tech=tech
        )
        total = project_crud.count_all(db, search=search, status=status, tech=tech)
        return [Project.model_validate(m) for m in models], total

    def get_project_by_id(self, project_id: int, db: Session) -> Optional[Project]:
        """根据 ID 获取项目详情，返回 None 表示不存在"""
        model = project_crud.get_by_id(db, project_id)
        if not model:
            return None
        return Project.model_validate(model)

    def create_project(self, project_create: ProjectCreate, db: Session) -> Project:
        """
        创建新项目

        Schema 校验已在路由层通过 Pydantic 完成，此处直接委托 CRUD。
        """
        model = project_crud.create(db, project_create)
        return Project.model_validate(model)

    def update_project(
        self, project_id: int, project_update: ProjectUpdate, db: Session
    ) -> Optional[Project]:
        """
        更新项目

        支持部分更新：只更新传入的非 None 字段。
        """
        model = project_crud.update(db, project_id, project_update)
        if not model:
            return None
        return Project.model_validate(model)

    def delete_project(self, project_id: int, db: Session) -> bool:
        """删除项目，返回是否成功"""
        return project_crud.delete(db, project_id)
