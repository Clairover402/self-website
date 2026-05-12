"""
项目路由

定义项目（作品集）管理操作的 REST API 端点。
处理项目的 CRUD 操作，包括创建、检索、更新和删除。

列表端点支持：分页（page/page_size）、搜索（search）、状态过滤（status）、技术栈过滤（tech）。

资源未找到时抛出 NotFoundException，由全局异常处理器统一返回 HTTP 404 + Result 格式。
"""

import math
from typing import Optional
from schemas.common import PaginationParams, PaginatedResult
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database.session import get_db
from schemas.project import Project, ProjectCreate, ProjectUpdate
from services.project_service import ProjectService
from utils.result import Result
from utils.exceptions import NotFoundException

router = APIRouter()
project_service = ProjectService()


@router.get("/", response_model=Result[PaginatedResult[Project]])
async def get_projects(
    # 分页参数：从查询字符串解析，带默认值和约束
    pagination: PaginationParams = Depends(),
    # 搜索参数：在名称和描述中模糊匹配
    search: Optional[str] = Query(default=None, description="搜索关键词"),
    # 状态过滤：精确匹配项目状态（如：进行中 / 已完成 / 维护中）
    status: Optional[str] = Query(default=None, description="按状态过滤"),
    # 技术栈过滤：精确匹配 JSON 数组中的技术值
    tech: Optional[str] = Query(default=None, description="按技术栈过滤"),
    db: Session = Depends(get_db),
):
    """
    获取项目列表（分页）

    支持组合过滤：可同时使用 search、status、tech 和分页参数。
    例如：GET /api/projects?page=1&page_size=10&status=已完成&tech=Python
    """
    projects, total = project_service.get_all_projects(
        db, offset=pagination.offset, limit=pagination.limit, search=search, status=status, tech=tech
    )

    # 计算总页数，向上取整
    total_pages = math.ceil(total / pagination.page_size) if total > 0 else 0

    return Result.ok(data=PaginatedResult[Project](
        items=projects,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages,
    ))


@router.get("/{project_id}", response_model=Result[Project])
async def get_project(project_id: int, db: Session = Depends(get_db)):
    """
    根据 ID 获取项目详情

    project_id 为整数，FastAPI 自动从路径参数解析并校验类型。
    资源不存在时抛出 NotFoundException，返回 HTTP 404。
    """
    project = project_service.get_project_by_id(project_id, db)
    if not project:
        raise NotFoundException(message="项目未找到", err_code="PROJECT_NOT_FOUND")
    return Result.ok(data=project)


@router.post("/", response_model=Result[Project])
async def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """
    创建新项目

    请求体由 Pydantic 自动校验字段完整性和类型。
    """
    new_project = project_service.create_project(project, db)
    return Result.ok(data=new_project)


@router.put("/{project_id}", response_model=Result[Project])
async def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db),
):
    """
    更新项目（部分更新）

    只更新请求体中传入的非 None 字段，未传入的字段保持不变。
    资源不存在时抛出 NotFoundException，返回 HTTP 404。
    """
    updated_project = project_service.update_project(project_id, project_update, db)
    if not updated_project:
        raise NotFoundException(message="项目未找到", err_code="PROJECT_NOT_FOUND")
    return Result.ok(data=updated_project)


@router.delete("/{project_id}", response_model=Result[dict])
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    """
    删除项目

    成功删除返回确认消息。
    项目不存在时抛出 NotFoundException，返回 HTTP 404。
    重复删除同一 ID 也会触发 404（幂等语义）。
    """
    success = project_service.delete_project(project_id, db)
    if not success:
        raise NotFoundException(message="项目未找到", err_code="PROJECT_NOT_FOUND")
    return Result.ok(data={"message": "项目删除成功"})