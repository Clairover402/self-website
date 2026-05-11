"""
项目路由

定义项目管理操作的 REST API 端点。
处理项目的 CRUD 操作，包括创建、检索、更新和删除。
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.session import get_db
from schemas.project import Project, ProjectCreate, ProjectUpdate
from services.project_service import ProjectService
from utils.result import Result

router = APIRouter()
project_service = ProjectService()


@router.get("/", response_model=Result[list[Project]])
async def get_projects(db: Session = Depends(get_db)):
    projects = project_service.get_all_projects(db)
    return Result.ok(data=projects, total=len(projects))


@router.get("/{project_id}", response_model=Result[Project])
async def get_project(project_id: int, db: Session = Depends(get_db)):
    project = project_service.get_project_by_id(project_id, db)
    if not project:
        return Result.fail(errorMsg="项目未找到", errCode="PROJECT_NOT_FOUND")
    return Result.ok(data=project)


@router.post("/", response_model=Result[Project])
async def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    new_project = project_service.create_project(project, db)
    return Result.ok(data=new_project)


@router.put("/{project_id}", response_model=Result[Project])
async def update_project(project_id: int, project_update: ProjectUpdate, db: Session = Depends(get_db)):
    updated_project = project_service.update_project(project_id, project_update, db)
    if not updated_project:
        return Result.fail(errorMsg="项目未找到", errCode="PROJECT_NOT_FOUND")
    return Result.ok(data=updated_project)


@router.delete("/{project_id}", response_model=Result[dict])
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    success = project_service.delete_project(project_id, db)
    if not success:
        return Result.fail(errorMsg="项目未找到", errCode="PROJECT_NOT_FOUND")
    return Result.ok(data={"message": "项目删除成功"})
