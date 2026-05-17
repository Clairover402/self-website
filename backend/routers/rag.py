"""
=============================================================================
RAG 公开路由层 (Router) — 仅聊天查询与对话记录
=============================================================================

知识库和文档的 CRUD 已迁移到 admin router（JWT 保护）。
本模块仅保留公开可用的：查询、知识库只读列表、对话记录。
"""

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse

from schemas.rag import (
    RAGQueryRequest,
    RAGQueryResponse,
    RAGEvaluateRequest,
    RAGEvaluateResponse,
    KnowledgeBase,
    RAGConversation,
)
from services.rag_service import RAGService
from utils.result import Result
from rag.resilience import rate_limiter, init_rate_limiter, CircuitOpenError
from core.config import settings

router = APIRouter()
rag_service = RAGService()

# 初始化限流器
if rate_limiter is None:
    init_rate_limiter(settings.RATE_LIMIT_QPS)


# =====================================================================
# 查询端点
# =====================================================================

@router.post("/query", response_model=Result[RAGQueryResponse])
async def query_rag(request: RAGQueryRequest):
    """RAG 查询（非流式）"""
    if rate_limiter and not rate_limiter.consume():
        return JSONResponse(
            status_code=429,
            content=Result.fail(errorMsg="系统繁忙，请稍后再试", errCode="RATE_LIMITED").model_dump(),
        )
    try:
        result = rag_service.query(request.question, request.knowledge_base_id, public_only=True)
    except CircuitOpenError:
        return JSONResponse(
            status_code=503,
            content=Result.fail(
                errorMsg="AI 服务暂时不可用（DeepSeek API 异常），请稍后再试或检查日志",
                errCode="SERVICE_UNAVAILABLE",
            ).model_dump(),
        )

    rag_service.save_conversation(
        kb_id=request.knowledge_base_id,
        user_query=request.question,
        answer=result.answer,
        sources=result.sources,
    )

    return Result.ok(data=result)


@router.post("/query/stream")
async def query_rag_stream(request: RAGQueryRequest):
    """RAG 查询（SSE 流式输出）"""
    if rate_limiter and not rate_limiter.consume():
        return JSONResponse(
            status_code=429,
            content=Result.fail(errorMsg="系统繁忙，请稍后再试", errCode="RATE_LIMITED").model_dump(),
        )

    async def event_stream():
        full_answer = ""
        try:
            yield "data: [THINKING]正在检索知识库..."

            for token in rag_service.query_stream(
                request.question, request.knowledge_base_id, public_only=True
            ):
                full_answer += token
                yield f"data: {token}\n\n"

            try:
                rag_service.save_conversation(
                    kb_id=request.knowledge_base_id,
                    user_query=request.question,
                    answer=full_answer,
                    sources=[],
                )
            except Exception:
                pass

            yield "data: [DONE]\n\n"
        except CircuitOpenError:
            yield "data: [ERROR]AI 服务暂时不可用（DeepSeek API 异常），请稍后再试或检查日志\n\n"
        except Exception as e:
            yield f"data: [ERROR]{str(e)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# =====================================================================
# 公开只读端点
# =====================================================================

@router.get("/knowledge-bases", response_model=Result[list[KnowledgeBase]])
async def get_knowledge_bases():
    """获取所有公开知识库列表（只读，供聊天选择知识库）"""
    kbs = rag_service.get_knowledge_bases(public_only=True)
    return Result.ok(data=kbs, total=len(kbs))


@router.get("/conversations", response_model=Result[list[RAGConversation]])
async def get_conversations(kb_id: str = Query(None, description="知识库 ID 过滤")):
    """获取对话记录"""
    conversations = rag_service.get_conversations(kb_id)
    return Result.ok(data=conversations, total=len(conversations))


# =====================================================================
# 评估端点
# =====================================================================

@router.post("/evaluate", response_model=Result[RAGEvaluateResponse])
async def evaluate_rag(request: RAGEvaluateRequest):
    """RAGAS 评估：运行查询并计算指标"""
    if rate_limiter and not rate_limiter.consume():
        return JSONResponse(
            status_code=429,
            content=Result.fail(errorMsg="系统繁忙，请稍后再试", errCode="RATE_LIMITED").model_dump(),
        )
    try:
        result = rag_service.evaluate_query(
            question=request.question,
            kb_id=request.knowledge_base_id,
            ground_truth=request.ground_truth,
        )
        return Result.ok(data=result)
    except CircuitOpenError:
        return JSONResponse(
            status_code=503,
            content=Result.fail(
                errorMsg="AI 服务暂时不可用（DeepSeek API 异常），请稍后再试或检查日志",
                errCode="SERVICE_UNAVAILABLE",
            ).model_dump(),
        )
