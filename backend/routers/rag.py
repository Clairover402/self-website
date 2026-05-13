"""
=============================================================================
RAG 路由层 (Router) — FastAPI REST API 端点
=============================================================================

【架构中的位置】
Router 是 MVC 中的 Controller 层：
- 接收 HTTP 请求
- 参数提取和校验（Pydantic 自动完成）
- 调用 Service 层
- 返回统一响应格式（Result[T]）

【类比 Java Spring Boot】
  @RestController
  @RequestMapping("/api/rag")
  public class RagController {
      @PostMapping("/query")
      public Result<RAGQueryResponse> query(@RequestBody RAGQueryRequest req) {
          return ragService.query(req);
      }
  }

【URL 设计规范】
所有端点前缀 /api/rag（在 main.py 中通过 prefix 注册）。
"""

from fastapi import APIRouter, File, UploadFile, Query
from fastapi.responses import StreamingResponse

from schemas.rag import (
    RAGQueryRequest,
    RAGQueryResponse,
    KnowledgeBase,
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    Document,
    DocumentUploadResponse,
    RAGConversation,
)
from services.rag_service import RAGService
from utils.result import Result

# APIRouter = 路由组，类似 Spring 的 @RequestMapping 分组
router = APIRouter()

# Service 实例（这里直接在模块层创建，没有用依赖注入）
# 生产环境中通常用 FastAPI 的 Depends() 做依赖注入，
# 但对这个项目规模，直接创建更简洁
rag_service = RAGService()


# =====================================================================
# 查询端点
# =====================================================================

@router.post("/query", response_model=Result[RAGQueryResponse])
async def query_rag(request: RAGQueryRequest):
    """
    RAG 查询（非流式）。

    POST /api/rag/query
    Body: {"question": "什么是RAG？", "knowledge_base_id": "xxx"}

    【response_model 的作用】
    FastAPI 自动将返回值序列化为 JSON，
    并根据 response_model 做类型校验和文档生成。
    相当于 Spring 的 @ResponseBody + Jackson 序列化。
    """
    result = rag_service.query(request.question, request.knowledge_base_id)

    # 自动保存对话记录（每次查询都记录，用于分析）
    rag_service.save_conversation(
        kb_id=request.knowledge_base_id,
        user_query=request.question,
        answer=result.answer,
        sources=result.sources,
    )

    return Result.ok(data=result)


@router.post("/query/stream")
async def query_rag_stream(request: RAGQueryRequest):
    """
    RAG 查询（SSE 流式输出）。

    POST /api/rag/query/stream
    Body: {"question": "什么是RAG？", "knowledge_base_id": "xxx"}

    【SSE (Server-Sent Events) 协议】
    一种 HTTP 长连接协议，服务端可以持续推送数据。
    格式：data: <内容>\n\n

    浏览器端用 EventSource 或 fetch + ReadableStream 消费。

    【类比 WebSocket】
    SSE 是单向的（服务器→客户端），比 WebSocket 更简单：
    - WebSocket：全双工，需要握手升级协议
    - SSE：基于 HTTP，自动重连，更轻量

    对于 RAG 这种"请求→流式回答"场景，SSE 更合适。

    【响应头说明】
    Cache-Control: no-cache      → 不要缓存
    Connection: keep-alive       → 保持连接
    X-Accel-Buffering: no        → 禁用 Nginx 缓冲（生产部署时有用）
    """
    async def event_stream():
        """
        Python 异步生成器 —— 流式输出的核心。

        async def + yield = 异步生成器
        类比 Java Reactor 的 Flux<String>：
            public Flux<String> stream() {
                return Flux.create(sink -> {
                    for (String token : llm.stream(prompt)) {
                        sink.next(token);
                    }
                    sink.complete();
                });
            }
        """
        full_answer = ""
        try:
            # 逐 token 推送到客户端
            for token in rag_service.query_stream(
                request.question, request.knowledge_base_id
            ):
                full_answer += token
                # SSE 格式：data: <内容>\n\n
                yield f"data: {token}\n\n"

            # 流结束后保存完整对话
            rag_service.save_conversation(
                kb_id=request.knowledge_base_id,
                user_query=request.question,
                answer=full_answer,
                sources=[],
            )
        except Exception as e:
            # 错误也通过 SSE 推送（前端可以展示错误提示）
            yield f"data: [ERROR] {str(e)}\n\n"
        finally:
            # [DONE] 是 SSE 的约定结束信号
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",  # SSE 的 MIME 类型
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# =====================================================================
# 知识库 CRUD 端点
# =====================================================================

@router.get("/knowledge-bases", response_model=Result[list[KnowledgeBase]])
async def get_knowledge_bases():
    """
    获取所有知识库。

    GET /api/rag/knowledge-bases
    """
    kbs = rag_service.get_knowledge_bases()
    return Result.ok(data=kbs, total=len(kbs))


@router.get("/knowledge-bases/{kb_id}", response_model=Result[KnowledgeBase])
async def get_knowledge_base(kb_id: str):
    """
    获取单个知识库详情。

    GET /api/rag/knowledge-bases/{kb_id}

    【路径参数 {kb_id}】
    FastAPI 自动从 URL 路径中提取参数，
    类似 Spring 的 @PathVariable。
    """
    kb = rag_service.get_knowledge_base_by_id(kb_id)
    if not kb:
        return Result.fail(errorMsg="知识库未找到", errCode="KB_NOT_FOUND")
    return Result.ok(data=kb)


@router.post("/knowledge-bases", response_model=Result[KnowledgeBase])
async def create_knowledge_base(kb: KnowledgeBaseCreate):
    """
    创建新知识库。

    POST /api/rag/knowledge-bases
    Body: {"name": "技术文档", "description": "存放技术相关文档"}
    """
    new_kb = rag_service.create_knowledge_base(kb)
    return Result.ok(data=new_kb)


@router.put("/knowledge-bases/{kb_id}", response_model=Result[KnowledgeBase])
async def update_knowledge_base(kb_id: str, kb_update: KnowledgeBaseUpdate):
    """
    更新知识库（支持部分更新）。

    PUT /api/rag/knowledge-bases/{kb_id}
    Body: {"name": "新名称"}（只传要改的字段）
    """
    updated_kb = rag_service.update_knowledge_base(kb_id, kb_update)
    if not updated_kb:
        return Result.fail(errorMsg="知识库未找到", errCode="KB_NOT_FOUND")
    return Result.ok(data=updated_kb)


@router.delete("/knowledge-bases/{kb_id}", response_model=Result[dict])
async def delete_knowledge_base(kb_id: str):
    """
    删除知识库（级联删除文档和向量）。

    DELETE /api/rag/knowledge-bases/{kb_id}
    """
    success = rag_service.delete_knowledge_base(kb_id)
    if not success:
        return Result.fail(errorMsg="知识库未找到", errCode="KB_NOT_FOUND")
    return Result.ok(data={"message": "知识库删除成功"})


# =====================================================================
# 文档管理端点
# =====================================================================

@router.post("/documents", response_model=Result[DocumentUploadResponse])
async def upload_document(
    kb_id: str = Query(..., description="知识库 ID"),
    file: UploadFile = File(...),
):
    """
    上传文档并自动执行 ingest。

    POST /api/rag/documents?kb_id=xxx
    Body: multipart/form-data (文件)

    【UploadFile 说明】
    FastAPI 的 UploadFile 封装了 Python 的文件上传处理：
    - file.filename：原始文件名
    - file.content_type：MIME 类型
    - await file.read()：读取文件内容到 bytes

    类比 Spring 的 MultipartFile。

    【Query(...) 的含义】
    ... 是 Python 的 Ellipsis，FastAPI 用它表示"必填参数"。
    query parameter 中的 kb_id 是必传的。
    """
    content = await file.read()
    result = rag_service.upload_document(
        kb_id=kb_id,
        filename=file.filename or "unknown",
        content=content,
        mime_type=file.content_type or "",
    )
    return Result.ok(data=result)


@router.get("/documents", response_model=Result[list[Document]])
async def get_documents(kb_id: str = Query(None, description="知识库 ID 过滤")):
    """
    获取文档列表。

    GET /api/rag/documents          → 所有文档
    GET /api/rag/documents?kb_id=xx → 按知识库过滤
    """
    docs = rag_service.get_documents(kb_id)
    return Result.ok(data=docs, total=len(docs))


@router.delete("/documents/{doc_id}", response_model=Result[dict])
async def delete_document(doc_id: str):
    """
    删除文档（同时从 MySQL 和 Qdrant 中清除）。

    DELETE /api/rag/documents/{doc_id}
    """
    success = rag_service.delete_document(doc_id)
    if not success:
        return Result.fail(errorMsg="文档未找到", errCode="DOC_NOT_FOUND")
    return Result.ok(data={"message": "文档删除成功"})


# =====================================================================
# 对话记录端点
# =====================================================================

@router.get("/conversations", response_model=Result[list[RAGConversation]])
async def get_conversations(kb_id: str = Query(None, description="知识库 ID 过滤")):
    """
    获取对话记录。

    GET /api/rag/conversations          → 所有对话
    GET /api/rag/conversations?kb_id=xx → 按知识库过滤
    """
    conversations = rag_service.get_conversations(kb_id)
    return Result.ok(data=conversations, total=len(conversations))