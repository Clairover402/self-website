"""
RAG 全链路耗时打点模块

提供 @timed(name) 装饰器和 TimingContext 上下文管理器，
from uuid import uuid4
基于 contextvars 确保每个请求独立计时，支持异步安全。
"""

import time
import logging
from functools import wraps
from contextvars import ContextVar
from typing import Optional

logger = logging.getLogger("rag.timing")

# 每个请求/任务独立的计时上下文
_timing_ctx: ContextVar[Optional["TimingContext"]] = ContextVar("timing_ctx", default=None)
_request_id: ContextVar[str] = ContextVar("request_id", default="")


class RequestContext:
    """请求级上下文，贯穿 Controller → Service → RAG 调用链"""
    __slots__ = ("request_id", "user_id")

    def __init__(self, request_id: str = "", user_id: str = ""):
        self.request_id = request_id or str(uuid4())[:8]
        self.user_id = user_id

    @staticmethod
    def current() -> "RequestContext":
        rid = _request_id.get()
        return RequestContext(request_id=rid) if rid else RequestContext()

    @staticmethod
    def set_request_id(rid: str) -> None:
        _request_id.set(rid)


class TimingContext:
    """单次请求的计时上下文，收集所有 @timed 记录"""

    def __init__(self, label: str = ""):
        self.label = label
        self.records: list[tuple[str, float]] = []

    def record(self, name: str, elapsed_ms: float):
        self.records.append((name, elapsed_ms))
        rid = _request_id.get() or "-"
        logger.info(f"[TIMING] [{rid}] {name}: {elapsed_ms:.1f}ms")

    def flush(self):
        """输出汇总耗时并清理"""
        if not self.records:
            return
        label_str = f" {self.label}" if self.label else ""
        total = sum(r[1] for r in self.records) if self.records else 0.0
        rid = _request_id.get() or "-"
        logger.info(f"[TOTAL{label_str}] [{rid}] {total:.1f}ms")
        self.records.clear()


def get_timing_ctx() -> TimingContext:
    """获取当前上下文的 TimingContext，不存在则创建"""
    ctx = _timing_ctx.get()
    if ctx is None:
        ctx = TimingContext()
        _timing_ctx.set(ctx)
    return ctx


def reset_timing_ctx(label: str = "") -> TimingContext:
    """重置并返回新的 TimingContext（用于每次查询/摄入的入口）"""
    ctx = TimingContext(label=label)
    _timing_ctx.set(ctx)
    return ctx


def timed(name: str):
    """装饰器：为函数调用计时并记录到 TimingContext"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            ctx = _timing_ctx.get()
            if ctx is None:
                return func(*args, **kwargs)
            start = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                elapsed = (time.perf_counter() - start) * 1000
                ctx.record(name, elapsed)
        return wrapper
    return decorator
