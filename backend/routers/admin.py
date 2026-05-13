"""
Admin router - JWT-protected management endpoints.

All endpoints except /login require Bearer token authentication.
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database.session import get_db
from core.auth import login_admin, verify_admin_token
from schemas.blog import Blog, BlogCreate, BlogUpdate
from schemas.project import ProjectCreate, ProjectUpdate
from schemas.award import AwardCreate, AwardUpdate
from schemas.contact import Contact
from services.blog_service import BlogService
from services.project_service import ProjectService
from services.award_service import AwardService
from models.contact import ContactModel
from pydantic import BaseModel
from utils.result import Result
from pydantic import BaseModel
from utils.exceptions import NotFoundException
from typing import Optional

router = APIRouter()
blog_service = BlogService()
project_service = ProjectService()
award_service = AwardService()


def require_admin(authorization: Optional[str] = Header(None)):
    """Dependency: verify Bearer token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = authorization[7:]
    if not verify_admin_token(token):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return True


# ===== Auth =====

class LoginRequest(BaseModel):
    password: str

@router.post("/login")
async def admin_login(body: LoginRequest):
    password = body.password
    """Login with admin password, returns JWT token."""
    token = login_admin(password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid password")
    return Result.ok(data={"token": token})

# ===== Blog CRUD =====

@router.post("/blogs", response_model=Result[Blog])
async def create_blog(blog: BlogCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return Result.ok(data=blog_service.create_blog(blog, db))

@router.put("/blogs/{slug}", response_model=Result[Blog])
async def update_blog(slug: str, blog: BlogUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    updated = blog_service.update_blog(slug, blog, db)
    if not updated:
        raise NotFoundException(message="Blog not found", err_code="BLOG_NOT_FOUND")
    return Result.ok(data=updated)

@router.delete("/blogs/{slug}", response_model=Result[dict])
async def delete_blog(slug: str, db: Session = Depends(get_db), _=Depends(require_admin)):
    success = blog_service.delete_blog(slug, db)
    if not success:
        raise NotFoundException(message="Blog not found", err_code="BLOG_NOT_FOUND")
    return Result.ok(data={"message": "Blog deleted"})


# ===== Project CRUD =====

@router.post("/projects")
async def create_project(project: ProjectCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return Result.ok(data=project_service.create_project(project, db))

@router.put("/projects/{id}")
async def update_project(id: int, project: ProjectUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    updated = project_service.update_project(id, project, db)
    if not updated:
        raise NotFoundException(message="Project not found", err_code="PROJECT_NOT_FOUND")
    return Result.ok(data=updated)

@router.delete("/projects/{id}")
async def delete_project(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    success = project_service.delete_project(id, db)
    if not success:
        raise NotFoundException(message="Project not found", err_code="PROJECT_NOT_FOUND")
    return Result.ok(data={"message": "Project deleted"})


# ===== Award CRUD =====

@router.post("/awards")
async def create_award(award: AwardCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return Result.ok(data=award_service.create_award(award, db))

@router.put("/awards/{id}")
async def update_award(id: int, award: AwardUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    updated = award_service.update_award(id, award, db)
    if not updated:
        raise NotFoundException(message="Award not found", err_code="AWARD_NOT_FOUND")
    return Result.ok(data=updated)

@router.delete("/awards/{id}")
async def delete_award(id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    success = award_service.delete_award(id, db)
    if not success:
        raise NotFoundException(message="Award not found", err_code="AWARD_NOT_FOUND")
    return Result.ok(data={"message": "Award deleted"})


# ===== Contacts =====

@router.get("/contacts")
async def list_contacts(db: Session = Depends(get_db), _=Depends(require_admin)):
    contacts = db.query(ContactModel).order_by(ContactModel.created_at.desc()).all()
    return Result.ok(data=[Contact.model_validate(c) for c in contacts])





