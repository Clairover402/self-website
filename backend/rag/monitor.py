"""
RAG 全链路耗时打点模块

提供 @timed(name) 装饰器和 TimingContext 上下文管理器，
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


class TimingContext:
    """单次请求的计时上下文，收集所有 @timed 记录"""

    def __init__(self, label: str = ""):
        self.label = label
        self.records: list[tuple[str, float]] = []

    def record(self, name: str, elapsed_ms: float):
        self.records.append((name, elapsed_ms))
        logger.info(f"[TIMING] {name}: {elapsed_ms:.1f}ms")

    def flush(self):
        """输出汇总耗时并清理"""
        if not self.records:
            return
        label_str = f" {self.label}" if self.label else ""
        total = sum(r[1] for r in self.records) if self.records else 0.0
        logger.info(f"[TOTAL{label_str}] {total:.1f}ms")
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
