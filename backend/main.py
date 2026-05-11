"""
RAG Personal Website - API Main Entry
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError

from core.config import settings
from core.logging_config import setup_logging
from core.exception_handlers import (
    app_exception_handler,
    validation_exception_handler,
    integrity_error_handler,
    generic_exception_handler,
)
from database.engine import init_db
from routers import blog, project, rag, health
from utils.exceptions import AppException


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize logging first, then database
    setup_logging(debug=settings.DEBUG)
    init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="Portfolio + Blog + RAG API",
    version=settings.API_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handlers
app.add_exception_handler(Exception, generic_exception_handler)
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)

# Routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(blog.router, prefix="/api/blogs", tags=["blogs"])
app.include_router(project.router, prefix="/api/projects", tags=["projects"])
app.include_router(rag.router, prefix="/api/rag", tags=["RAG"])


@app.get("/", tags=["root"])
async def root():
    return {"message": "Welcome to RAG Personal Website API"}
