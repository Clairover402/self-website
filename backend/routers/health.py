"""
健康检查路由

提供健康监控和状态检查的端点。
"""

from fastapi import APIRouter
from utils.result import Result

router = APIRouter()


@router.get("/health", response_model=Result[dict])
async def health_check():
    return Result.ok(data={"status": "healthy", "service": "RAG 个人网站 API"})
