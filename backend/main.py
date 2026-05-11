"""
RAG ������վ API �����

��ģ����Ϊ FastAPI Ӧ�õ�����ڣ����ú������á��м����·�ɡ�

������
    uvicorn main:app --reload --port 8000

API �ĵ���
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
from core.logging_config import setup_logging
from core.exception_handlers import (
    app_exception_handler,
    validation_exception_handler,
    starlette_http_exception_handler,
    integrity_error_handler,
    generic_exception_handler,
)
from database.engine import init_db
from routers import blog, project, rag, health, award
from utils.exceptions import AppException


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Ӧ���������ڹ���

    ���ʱ����ʼ����־ϵͳ��Ȼ���ʼ�����ݿ��ṹ��
    create_all ֻ�������ڵı����Ӱ���������ݡ�
    """
    # ��ʼ����־ϵͳ����־������ settings.DEBUG ����
    setup_logging(debug=settings.DEBUG)
    # ��ʼ�����ݿ��ṹ
    init_db()
    yield


# ���� FastAPI Ӧ��ʵ��
app = FastAPI(
    title=settings.APP_NAME,
    description="������Ʒ�� + �������� + AI ˽��֪ʶ�⣨RAG������һ�ĸ߶˸��˹������ API",
    version=settings.API_VERSION,
    docs_url="/api/docs",   # Swagger UI ·��
    redoc_url="/api/redoc", # ReDoc ·��
    lifespan=lifespan,
)

# ===== �м��ע�� =====

# CORS �м��������������Դ�Ŀ������󣨿����׶�ȫ��ͨ��
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== ȫ���쳣������ע�� =====
# ע�⣺FastAPI ��ע��˳������ƥ�䣬��ע������ȼ�����
# ���ͨ�� Exception ����ע�ᣨ������ȼ����������쳣��ע�ᣨ�������ȼ���

app.add_exception_handler(Exception, generic_exception_handler)
app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)

# ===== ·��ע�� =====

# ������飺GET /api/health
app.include_router(health.router, prefix="/api", tags=["�������"])

# ���͹����CRUD �˵���ص� /api/blogs
app.include_router(blog.router, prefix="/api/blogs", tags=["����"])

# ��Ŀ�����CRUD �˵���ص� /api/projects
app.include_router(project.router, prefix="/api/projects", tags=["��Ŀ"])

# RAG ֪ʶ�⣺׮����˵���ص� /api/rag������ʵ�֣�
app.include_router(rag.router, prefix="/api/rag", tags=["RAG"])

# 奖项管理：CRUD 端点挂载到 /api/awards
app.include_router(award.router, prefix="/api/awards", tags=["奖项"])


@app.get("/", tags=["��·��"])
async def root():
    """��·�������ػ�ӭ��Ϣ"""
    return {"message": "��ӭ���� RAG ������վ API"}