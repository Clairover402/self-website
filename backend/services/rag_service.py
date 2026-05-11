"""
RAG 服务模块（桩代码）

RAG 功能尚未实现。二期使用 Qdrant 向量数据库实现向量存储与检索。
当前所有方法返回空数据。
"""

from typing import Optional, List
from datetime import datetime
from schemas.rag import (
    RAGQueryResponse,
    KnowledgeBase,
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    Document,
    DocumentUploadResponse,
    RAGConversation
)


class RAGService:

    def __init__(self):
        pass

    def query(self, question: str, knowledge_base_id: Optional[str] = None) -> RAGQueryResponse:
        return RAGQueryResponse(
            answer=f"这是针对问题 '{question}' 的回答。由于 RAG 功能尚未完全实现，这是一个示例响应。",
            sources=[],
            confidence=0.0
        )

    def get_knowledge_bases(self) -> List[KnowledgeBase]:
        return []

    def get_knowledge_base_by_id(self, kb_id: str) -> Optional[KnowledgeBase]:
        return None

    def create_knowledge_base(self, kb_create: KnowledgeBaseCreate) -> KnowledgeBase:
        now = datetime.now()
        return KnowledgeBase(
            id="stub-id",
            name=kb_create.name,
            description=kb_create.description,
            is_default=kb_create.is_default or False,
            created_at=now,
            updated_at=now
        )

    def update_knowledge_base(self, kb_id: str, kb_update: KnowledgeBaseUpdate) -> Optional[KnowledgeBase]:
        return None

    def delete_knowledge_base(self, kb_id: str) -> bool:
        return True

    def upload_document(self, kb_id: str, filename: str, file_type: str, file_size: int) -> DocumentUploadResponse:
        return DocumentUploadResponse(message="文档上传成功（桩代码）", document_id="stub-doc-id")

    def get_documents(self, kb_id: Optional[str] = None) -> List[Document]:
        return []

    def delete_document(self, doc_id: str) -> bool:
        return True

    def get_conversations(self, kb_id: Optional[str] = None) -> List[RAGConversation]:
        return []