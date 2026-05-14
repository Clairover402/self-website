"""
RAG 个人网站 API 入口

该模块为 FastAPI 应用的入口点，负责应用配置、中间件和路由注册。

启动命令：
    uvicorn main:app --reload --port 8000

API 文档：
    Swagger UI:  http://localhost:8000/api/docs
    ReDoc:       http://localhost:8000/api/redoc
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

from core.config import settings
from core.auth import check_admin_security
from core.logging_config import setup_logging
from core.exception_handlers import (
    app_exception_handler,
    validation_exception_handler,
    starlette_http_exception_handler,
    integrity_error_handler,
    generic_exception_handler,
)
from database.engine import init_db
from routers import blog, project, rag, health, award, contact, admin
from utils.exceptions import AppException


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(debug=settings.DEBUG)
    check_admin_security()
    init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="个人作品集 + 技术博客 + AI 私有知识库（RAG）于一体的高端个人网站 API",
    version=settings.API_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# ===== CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Exception Handlers =====
app.add_exception_handler(Exception, generic_exception_handler)
app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)

# ===== Routes =====
app.include_router(health.router, prefix="/api", tags=["健康检查"])
app.include_router(blog.router, prefix="/api/blogs", tags=["博客"])
app.include_router(project.router, prefix="/api/projects", tags=["项目"])
app.include_router(rag.router, prefix="/api/rag", tags=["RAG"])

# Admin CRUD (JWT protected)
app.include_router(admin.router, prefix="/api/admin", tags=["管理后台"])

# Contact form
app.include_router(contact.router, prefix="/api/contact", tags=["联系方式"])

# Awards
app.include_router(award.router, prefix="/api/awards", tags=["奖项"])


@app.get("/", tags=["根路径"])
async def root():
    return {"message": "欢迎访问 RAG 个人网站 API"}
