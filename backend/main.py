"""
RAG 个人网站 API 主入口

此模块作为 FastAPI 应用的主入口，设置核心配置、中间件和路由。
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from database.engine import init_db
from routers import blog, project, rag, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="个人作品集 + 技术博客 + AI 私有知识库（RAG）三合一的高端个人官网后端 API",
    version=settings.API_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["健康检查"])
app.include_router(blog.router, prefix="/api/blogs", tags=["博客"])
app.include_router(project.router, prefix="/api/projects", tags=["项目"])
app.include_router(rag.router, prefix="/api/rag", tags=["RAG"])


@app.get("/", tags=["根路由"])
async def root():
    return {"message": "欢迎访问 RAG 个人网站 API"}
