"""
项目 CRUD 操作模块

提供作品集项目的数据库增删改查操作。
使用 SQLAlchemy 2.0 风格的 select() 语句替代已废弃的 session.query()。
所有方法接收 Session 实例作为依赖注入，便于测试时替换。

分页与过滤说明：
- 分页通过 offset/limit 实现，offset 从 0 开始计算
- 搜索使用 SQL LIKE 对名称和描述做模糊匹配
- 技术栈过滤使用 MySQL JSON_CONTAINS 函数
- 状态过滤为精确匹配
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from models.project import ProjectModel
from schemas.project import ProjectCreate, ProjectUpdate


def get_all(
    db: Session,
    offset: int = 0,
    limit: int = 10,
    search: Optional[str] = None,
    status: Optional[str] = None,
    tech: Optional[str] = None,
) -> list[ProjectModel]:
    """
    获取项目列表（支持分页、搜索、状态过滤、技术栈过滤）

    参数：
        offset: SQL OFFSET 值（由调用方根据 page 计算）
        limit: 每页最大条数
        search: 模糊搜索关键词，同时匹配名称和描述
        status: 项目状态精确过滤（如：进行中 / 已完成 / 维护中）
        tech: 技术栈过滤，使用 JSON_CONTAINS 检查 techs 数组是否包含指定值

    所有过滤参数均为可选，不传时返回全部数据。
    """
    stmt = select(ProjectModel)

    # 搜索过滤：在名称和描述中进行 LIKE 模糊匹配
    if search:
        like_pattern = f"%{search}%"
        stmt = stmt.where(
            ProjectModel.name.like(like_pattern)
            | ProjectModel.description.like(like_pattern)
        )

    # 状态过滤：精确匹配项目状态字段
    if status:
        stmt = stmt.where(ProjectModel.status == status)

    # 技术栈过滤：检查 JSON 数组是否包含指定技术
    # 使用 MySQL 的 JSON_CONTAINS 函数
    if tech:
        stmt = stmt.where(
            func.json_contains(ProjectModel.techs, f'"{tech}"')
        )

    # 分页：先按创建时间倒序排列，再截取指定页
    stmt = stmt.order_by(ProjectModel.created_at.desc()).offset(offset).limit(limit)
    return db.execute(stmt).scalars().all()


def count_all(
    db: Session,
    search: Optional[str] = None,
    status: Optional[str] = None,
    tech: Optional[str] = None,
) -> int:
    """
    统计符合条件的项目总数

    与 get_all 使用完全相同的过滤条件，确保 total 值准确。
    使用 func.count() 在数据库端计数，避免传输全部数据。
    """
    stmt = select(func.count(ProjectModel.id))

    if search:
        like_pattern = f"%{search}%"
        stmt = stmt.where(
            ProjectModel.name.like(like_pattern)
            | ProjectModel.description.like(like_pattern)
        )

    if status:
        stmt = stmt.where(ProjectModel.status == status)

    if tech:
        stmt = stmt.where(
            func.json_contains(ProjectModel.techs, f'"{tech}"')
        )

    return db.execute(stmt).scalar() or 0


def get_by_id(db: Session, project_id: int) -> Optional[ProjectModel]:
    """
    根据 ID 查找单个项目

    项目使用自增整数 ID 作为主键（与博客的 slug 策略不同）。
    返回 None 表示未找到对应项目。
    """
    stmt = select(ProjectModel).where(ProjectModel.id == project_id)
    return db.execute(stmt).scalars().first()


def create(db: Session, project_create: ProjectCreate) -> ProjectModel:
    """
    创建新项目

    从 Pydantic Schema（已通过路由层校验）构造 ORM 实例。
    features 和 techs 提供默认空列表，避免 NULL 值影响前端渲染。
    创建后执行 commit + refresh 确保数据库生成的 id、时间戳回填到实例。
    """
    project = ProjectModel(
        name=project_create.name,
        description=project_create.description,
        icon=project_create.icon,
        status=project_create.status,
        year=project_create.year,
        full_description=project_create.full_description,
        features=project_create.features or [],  # 无特性时默认空列表
        techs=project_create.techs or [],          # 无技术栈时默认空列表
        demo_url=project_create.demo_url,
        repo_url=project_create.repo_url,
    )
    db.add(project)
    db.commit()       # 写入数据库
    db.refresh(project)  # 回填数据库生成的 id、created_at、updated_at
    return project


def update(db: Session, project_id: int, project_update: ProjectUpdate) -> Optional[ProjectModel]:
    """
    更新现有项目

    使用 model_dump(exclude_unset=True) 实现部分更新（PATCH 语义），
    只更新客户端实际发送的字段。
    更新时自动刷新 updated_at 时间戳（与 BlogModel 行为一致）。
    返回 None 表示项目不存在。
    """
    project = get_by_id(db, project_id)
    if not project:
        return None

    # exclude_unset=True：只取客户端显式传入的字段
    update_data = project_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)

    # 手动刷新更新时间戳，确保 updated_at 反映最近一次修改
    project.updated_at = datetime.now()
    db.commit()
    db.refresh(project)
    return project


def delete(db: Session, project_id: int) -> bool:
    """
    删除项目

    先查找再删除，返回 True 表示删除成功，False 表示项目不存在。
    不会抛出异常，由路由层根据返回值决定响应。
    """
    project = get_by_id(db, project_id)
    if not project:
        return False
    db.delete(project)
    db.commit()
    return True
