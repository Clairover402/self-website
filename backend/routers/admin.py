"""
Admin router - JWT-protected management endpoints.

All endpoints except /login require Bearer token authentication.
"""
from fastapi import APIRouter, Depends, File, HTTPException, Header, Query, UploadFile
from sqlalchemy.orm import Session
from database.session import get_db
from core.auth import login_admin, verify_admin_token
from schemas.blog import Blog, BlogCreate, BlogUpdate
from schemas.project import ProjectCreate, ProjectUpdate
from schemas.award import AwardCreate, AwardUpdate
from schemas.contact import Contact
from schemas.rag import (
    KnowledgeBase,
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    Document,
    DocumentUploadResponse,
)
from services.blog_service import BlogService
from services.project_service import ProjectService
from services.award_service import AwardService
from services.rag_service import RAGService
from models.contact import ContactModel
from pydantic import BaseModel
from utils.result import Result
from utils.exceptions import NotFoundException
from typing import Optional

router = APIRouter()
blog_service = BlogService()
project_service = ProjectService()
award_service = AwardService()
rag_service = RAGService()


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


# ===== RAG Knowledge Base CRUD =====

@router.get("/rag/knowledge-bases", response_model=Result[list[KnowledgeBase]])
async def admin_get_knowledge_bases(_=Depends(require_admin)):
    """获取所有知识库列表"""
    kbs = rag_service.get_knowledge_bases()
    return Result.ok(data=kbs, total=len(kbs))


@router.get("/rag/knowledge-bases/{kb_id}", response_model=Result[KnowledgeBase])
async def admin_get_knowledge_base(kb_id: str, _=Depends(require_admin)):
    """获取单个知识库详情"""
    kb = rag_service.get_knowledge_base_by_id(kb_id)
    if not kb:
        return Result.fail(errorMsg="知识库未找到", errCode="KB_NOT_FOUND")
    return Result.ok(data=kb)


@router.post("/rag/knowledge-bases", response_model=Result[KnowledgeBase])
async def admin_create_knowledge_base(kb: KnowledgeBaseCreate, _=Depends(require_admin)):
    """创建新知识库"""
    new_kb = rag_service.create_knowledge_base(kb)
    return Result.ok(data=new_kb)


@router.put("/rag/knowledge-bases/{kb_id}", response_model=Result[KnowledgeBase])
async def admin_update_knowledge_base(kb_id: str, kb_update: KnowledgeBaseUpdate, _=Depends(require_admin)):
    """更新知识库（支持部分更新）"""
    updated_kb = rag_service.update_knowledge_base(kb_id, kb_update)
    if not updated_kb:
        return Result.fail(errorMsg="知识库未找到", errCode="KB_NOT_FOUND")
    return Result.ok(data=updated_kb)


@router.delete("/rag/knowledge-bases/{kb_id}", response_model=Result[dict])
async def admin_delete_knowledge_base(kb_id: str, _=Depends(require_admin)):
    """删除知识库（级联删除文档和向量）"""
    success = rag_service.delete_knowledge_base(kb_id)
    if not success:
        return Result.fail(errorMsg="知识库未找到", errCode="KB_NOT_FOUND")
    return Result.ok(data={"message": "知识库删除成功"})


# ===== RAG Document CRUD =====

@router.get("/rag/documents", response_model=Result[list[Document]])
async def admin_get_documents(kb_id: str = Query(None, description="知识库 ID 过滤"), _=Depends(require_admin)):
    """获取文档列表"""
    docs = rag_service.get_documents(kb_id)
    return Result.ok(data=docs, total=len(docs))


@router.post("/rag/documents", response_model=Result[DocumentUploadResponse])
async def admin_upload_document(
    kb_id: str = Query(..., description="知识库 ID"),
    file: UploadFile = File(...),
    _=Depends(require_admin),
):
    """上传文档并自动执行 ingest"""
    content = await file.read()
    result = rag_service.upload_document(
        kb_id=kb_id,
        filename=file.filename or "unknown",
        content=content,
        mime_type=file.content_type or "",
    )
    return Result.ok(data=result)


@router.delete("/rag/documents/{doc_id}", response_model=Result[dict])
async def admin_delete_document(doc_id: str, _=Depends(require_admin)):
    """删除文档（同时从 MySQL 和 Qdrant 中清除）"""
    success = rag_service.delete_document(doc_id)
    if not success:
        return Result.fail(errorMsg="文档未找到", errCode="DOC_NOT_FOUND")
    return Result.ok(data={"message": "文档删除成功"})
