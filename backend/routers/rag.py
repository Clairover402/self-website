"""
RAG 路由

定义 RAG（检索增强生成）操作的 REST API 端点。
包括知识库管理、文档上传和 AI 查询功能的端点。
"""

from fastapi import APIRouter, File, UploadFile
from schemas.rag import (
    RAGQueryRequest,
    RAGQueryResponse,
    KnowledgeBase,
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    Document,
    DocumentUploadResponse,
    RAGConversation
)
from services.rag_service import RAGService
from utils.result import Result

router = APIRouter()
rag_service = RAGService()


@router.post("/query", response_model=Result[RAGQueryResponse])
async def query_rag(request: RAGQueryRequest):
    result = rag_service.query(request.question, request.knowledge_base_id)
    return Result.ok(data=result)


@router.get("/knowledge-bases", response_model=Result[list[KnowledgeBase]])
async def get_knowledge_bases():
    kbs = rag_service.get_knowledge_bases()
    return Result.ok(data=kbs, total=len(kbs))


@router.get("/knowledge-bases/{kb_id}", response_model=Result[KnowledgeBase])
async def get_knowledge_base(kb_id: str):
    kb = rag_service.get_knowledge_base_by_id(kb_id)
    if not kb:
        return Result.fail(errorMsg="知识库未找到", errCode="KB_NOT_FOUND")
    return Result.ok(data=kb)


@router.post("/knowledge-bases", response_model=Result[KnowledgeBase])
async def create_knowledge_base(kb: KnowledgeBaseCreate):
    new_kb = rag_service.create_knowledge_base(kb)
    return Result.ok(data=new_kb)


@router.put("/knowledge-bases/{kb_id}", response_model=Result[KnowledgeBase])
async def update_knowledge_base(kb_id: str, kb_update: KnowledgeBaseUpdate):
    updated_kb = rag_service.update_knowledge_base(kb_id, kb_update)
    if not updated_kb:
        return Result.fail(errorMsg="知识库未找到", errCode="KB_NOT_FOUND")
    return Result.ok(data=updated_kb)


@router.delete("/knowledge-bases/{kb_id}", response_model=Result[dict])
async def delete_knowledge_base(kb_id: str):
    success = rag_service.delete_knowledge_base(kb_id)
    if not success:
        return Result.fail(errorMsg="知识库未找到", errCode="KB_NOT_FOUND")
    return Result.ok(data={"message": "知识库删除成功"})


@router.post("/documents", response_model=Result[DocumentUploadResponse])
async def upload_document(kb_id: str, file: UploadFile = File(...)):
    result = rag_service.upload_document(
        kb_id=kb_id,
        filename=file.filename,
        file_type=file.content_type,
        file_size=0
    )
    return Result.ok(data=result)


@router.get("/documents", response_model=Result[list[Document]])
async def get_documents(kb_id: str = None):
    docs = rag_service.get_documents(kb_id)
    return Result.ok(data=docs, total=len(docs))


@router.delete("/documents/{doc_id}", response_model=Result[dict])
async def delete_document(doc_id: str):
    success = rag_service.delete_document(doc_id)
    if not success:
        return Result.fail(errorMsg="文档未找到", errCode="DOC_NOT_FOUND")
    return Result.ok(data={"message": "文档删除成功"})


@router.get("/conversations", response_model=Result[list[RAGConversation]])
async def get_conversations(kb_id: str = None):
    conversations = rag_service.get_conversations(kb_id)
    return Result.ok(data=conversations, total=len(conversations))
