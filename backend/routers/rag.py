"""
=============================================================================
RAG 公开路由层 (Router) — 仅聊天查询与对话记录
=============================================================================

知识库和文档的 CRUD 已迁移到 admin router（JWT 保护）。
本模块仅保留公开可用的：查询、知识库只读列表、对话记录。
"""

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from schemas.rag import (
    RAGQueryRequest,
    RAGQueryResponse,
    KnowledgeBase,
    RAGConversation,
)
from services.rag_service import RAGService
from utils.result import Result

router = APIRouter()
rag_service = RAGService()


# =====================================================================
# 查询端点
# =====================================================================

@router.post("/query", response_model=Result[RAGQueryResponse])
async def query_rag(request: RAGQueryRequest):
    """RAG 查询（非流式）"""
    result = rag_service.query(request.question, request.knowledge_base_id)

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
    async def event_stream():
        full_answer = ""
        try:
            for token in rag_service.query_stream(
                request.question, request.knowledge_base_id
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
    """获取所有知识库列表（只读，供聊天选择知识库）"""
    kbs = rag_service.get_knowledge_bases()
    return Result.ok(data=kbs, total=len(kbs))


@router.get("/conversations", response_model=Result[list[RAGConversation]])
async def get_conversations(kb_id: str = Query(None, description="知识库 ID 过滤")):
    """获取对话记录"""
    conversations = rag_service.get_conversations(kb_id)
    return Result.ok(data=conversations, total=len(conversations))
