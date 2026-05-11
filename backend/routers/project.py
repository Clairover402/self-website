"""
项目路由

定义项目（作品集）管理操作的 REST API 端点。
处理项目的 CRUD 操作，包括创建、检索、更新和删除。

列表端点支持：分页（page/page_size）、搜索（search）、状态过滤（status）、技术栈过滤（tech）。
"""

import math
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database.session import get_db
from schemas.project import Project, ProjectCreate, ProjectUpdate
from services.project_service import ProjectService
from utils.result import Result

router = APIRouter()
project_service = ProjectService()


@router.get("/", response_model=Result[dict])
async def get_projects(
    # 分页参数：从查询字符串解析，带默认值和约束
    page: int = Query(default=1, ge=1, description="页码（从 1 开始）"),
    page_size: int = Query(default=10, ge=1, le=100, description="每页条数（1-100）"),
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
    # 将页码转换为数据库 offset
    offset = (page - 1) * page_size

    projects, total = project_service.get_all_projects(
        db, offset=offset, limit=page_size, search=search, status=status, tech=tech
    )

    # 计算总页数，向上取整
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return Result.ok(data={
        "items": projects,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    })


@router.get("/{project_id}", response_model=Result[Project])
async def get_project(project_id: int, db: Session = Depends(get_db)):
    """
    根据 ID 获取项目详情

    project_id 为整数，FastAPI 自动从路径参数解析并校验类型。
    """
    project = project_service.get_project_by_id(project_id, db)
    if not project:
        return Result.fail(errorMsg="项目未找到", errCode="PROJECT_NOT_FOUND")
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
    """
    updated_project = project_service.update_project(project_id, project_update, db)
    if not updated_project:
        return Result.fail(errorMsg="项目未找到", errCode="PROJECT_NOT_FOUND")
    return Result.ok(data=updated_project)


@router.delete("/{project_id}", response_model=Result[dict])
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    """
    删除项目

    成功删除返回确认消息，项目不存在返回错误。
    """
    success = project_service.delete_project(project_id, db)
    if not success:
        return Result.fail(errorMsg="项目未找到", errCode="PROJECT_NOT_FOUND")
    return Result.ok(data={"message": "项目删除成功"})
