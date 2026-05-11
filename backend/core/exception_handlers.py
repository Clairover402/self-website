"""
全局异常处理器

将各类异常统一转换为 Result.fail() 格式的 JSON 响应。
注册到 FastAPI app 后，所有未在路由中捕获的异常都会流经此模块。

处理顺序：
1. AppException（及其子类）→ 使用异常自带的 message/err_code/status_code
2. RequestValidationError（Pydantic 校验失败）→ 提取字段级错误详情
3. IntegrityError（数据库约束冲突）→ 解析为业务友好的冲突提示
4. Exception（兜底）→ 模糊的 500 错误，避免泄漏敏感信息
"""

import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from utils.exceptions import AppException
from utils.result import Result

logger = logging.getLogger(__name__)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    处理应用层自定义异常

    将 AppException 及其子类（NotFoundException、ConflictException 等）
    转换为统一的 Result.fail() JSON 响应。
    HTTP 状态码使用异常自带的 status_code（而非始终 200），
    便于 HTTP 客户端和监控工具正确识别错误。
    """
    logger.warning(
        "业务异常 | path=%s | err_code=%s | message=%s",
        request.url.path,
        exc.err_code,
        exc.message,
    )
    result = Result.fail(errorMsg=exc.message, errCode=exc.err_code)
    return JSONResponse(
        status_code=exc.status_code,
        content=result.model_dump(),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    处理 Pydantic 请求校验失败

    当请求体或查询参数不符合 Schema 定义时，FastAPI 自动抛出此异常。
    从原始错误中提取每个字段的具体校验失败信息，拼接为可读的错误消息。
    """
    # 提取第一个校验错误的字段和原因
    errors = exc.errors()
    if errors:
        first_error = errors[0]
        # loc 是错误位置的路径元组，如 ("body", "title") 或 ("query", "page")
        field = " -> ".join(str(loc) for loc in first_error.get("loc", []))
        msg = first_error.get("msg", "校验失败")
        error_message = f"{field}: {msg}"
    else:
        error_message = "请求参数校验失败"

    logger.warning("参数校验失败 | path=%s | detail=%s", request.url.path, error_message)
    result = Result.fail(errorMsg=error_message, errCode="VALIDATION_ERROR")
    return JSONResponse(
        status_code=422,
        content=result.model_dump(),
    )


async def integrity_error_handler(
    request: Request, exc: IntegrityError
) -> JSONResponse:
    """
    处理数据库完整性约束冲突

    常见场景：
    - 重复 slug（UNIQUE 约束）
    - 外键引用不存在
    - NOT NULL 字段缺失

    将底层数据库错误转换为业务友好的提示信息。
    原始异常详情通过日志记录，不直接暴露给客户端。
    """
    # 提取原始数据库错误消息用于日志分析和日志记录
    orig = str(exc.orig) if exc.orig else str(exc)
    logger.error("数据库完整性冲突 | path=%s | detail=%s", request.url.path, orig)

    # 根据错误类型返回不同的用户提示
    # duplicate entry 是 MySQL 中重复键冲突的特征消息
    if "Duplicate entry" in orig or "UNIQUE constraint" in orig:
        user_message = "数据已存在，请检查唯一字段（如 slug）是否重复"
        err_code = "DUPLICATE_ENTRY"
    else:
        user_message = "数据操作冲突，请检查输入数据"
        err_code = "INTEGRITY_ERROR"

    result = Result.fail(errorMsg=user_message, errCode=err_code)
    return JSONResponse(
        status_code=409,
        content=result.model_dump(),
    )


async def generic_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """
    兜底异常处理器

    捕获所有未被以上处理器覆盖的异常。
    返回模糊的 500 错误，避免泄漏堆栈信息等敏感数据。
    完整异常详情记录在服务端日志中，供开发排查。
    """
    logger.exception("未预期的服务器错误 | path=%s", request.url.path)
    result = Result.fail(errorMsg="服务器内部错误", errCode="INTERNAL_ERROR")
    return JSONResponse(
        status_code=500,
        content=result.model_dump(),
    )
