
"""
RAG 弹性模块 - 限流 + 熔断 + 降级

提供生产级保护机制：
- TokenBucket: 令牌桶限流，默认 100 QPS
- CircuitBreaker: 三态熔断器，连续失败后自动开闸
- LLMFallback: LLM 降级调用封装
"""

import time
import logging
import enum
from threading import Lock
from typing import Optional, Callable, Any

logger = logging.getLogger("rag.resilience")


# =========================================================================
# 令牌桶限流
# =========================================================================

class TokenBucket:
    """
    令牌桶算法限流器。

    【生活中的类比：景区售票】
    想象一个热门景区，每小时只能接待 100 名游客。售票处每小时发放 100 张门票。
    - 游客来了 → 有票就进，没票就在门口排队或被劝返
    - 门票不会永远攒着 → 桶有上限（burst），防止"囤票"
    - 没人来的时候 → 门票累积到上限后不再增加，不会让下一小时进来 200 人

    【令牌桶 vs 漏桶】
    这是两种经典限流算法：
    - 令牌桶（Token Bucket）：以恒定速率"放入"令牌，请求"取出"令牌。
      允许突发流量——桶里攒了多少令牌，就能瞬间处理多少请求。
    - 漏桶（Leaky Bucket）：以恒定速率"漏出"请求。不允许突发。
    令牌桶更适合 Web API：偶尔的流量尖峰（如首页被分享）应该被允许，
    只要平均 QPS 不超标。

    【为什么不用线程安全的 Queue？】
    令牌桶不需要真的存 N 个令牌对象。
    用数学公式即可：tokens = min(burst, current_tokens + elapsed * rate)
    线程安全只需一把 Lock 保护浮点数更新。这在 Java 中类似 synchronized。
    """

    def __init__(self, rate: float = 100, burst: Optional[float] = None):
        """
        初始化令牌桶。

        参数：
          rate  — 令牌生成速率（个/秒），即长期平均 QPS 上限，默认 100
          burst — 桶容量（最大令牌数），即允许的突发流量上限，默认等于 rate

        初始状态：桶满（tokens = burst），即服务刚启动时允许一次突发。
        """
        self.rate = rate                  # 令牌生成速率（每秒）
        self.burst = burst or rate        # 桶容量（允许突发），未指定时与 rate 相同
        self.tokens = self.burst          # 当前令牌数，初始为满桶
        self.last_refill = time.monotonic()  # 上次补充令牌的时间戳
        self._lock = Lock()               # 线程锁（Python 的 GIL 不保证原子性）

    def consume(self, tokens: float = 1) -> bool:
        """
        尝试消费令牌，返回是否成功。

        【执行步骤】
        1. 计算距离上次补充过去了多久（elapsed）
        2. 按 rate 补充令牌：new_tokens = old_tokens + elapsed * rate
           - 例：rate=100，0.5 秒过去了 → 补充 50 个令牌
        3. 截断到 burst 上限（不能超过桶容量）
        4. 如果当前令牌数 >= 需要的令牌数 → 消费成功
           否则 → 返回 False，调用方通常返回 HTTP 429

        【为什么用 time.monotonic() 而不是 time.time()？】
        monotonic() 是单调递增时钟，不受系统时间调整影响。
        如果运维手动改了服务器时间，time.time() 可能导致 elapsed 为负数，
        令牌计算完全错误。monotonic() 杜绝了这个问题。
        """
        with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_refill
            # 核心公式：补充 = 流逝时间 × 速率，但不能超过桶容量
            self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
            self.last_refill = now
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    @property
    def available(self) -> float:
        """
        当前可用令牌数（只读属性）。

        主要用于监控面板、日志输出，了解当前限流器状态。
        例：available=0 时说明流量已打满，后续请求会被拒绝。
        """
        with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_refill
            return min(self.burst, self.tokens + elapsed * self.rate)


# =========================================================================
# 熔断器
# =========================================================================

class CircuitState(enum.Enum):
    """
    熔断器三态枚举。

    【状态含义】
    - CLOSED   : 正常状态。所有请求正常通过，失败计数器累加。
    - OPEN     : 熔断状态。直接拒绝所有请求（抛出 CircuitOpenError），不给下游增加压力。
    - HALF_OPEN: 半开状态。放行一个试探请求，成功→CLOSED，失败→重新 OPEN。

    【为什么需要 HALF_OPEN？】
    如果没有半开状态，熔断器只能依赖定时器"盲目"恢复。
    HALF_OPEN 实现了"先试探，再决定"的策略：用一个真实请求去探测下游是否已经恢复。
    这比纯粹靠超时恢复更安全——如果下游还没好，不会让所有请求都失败一遍。
    """
    CLOSED = "closed"       # 正常
    OPEN = "open"           # 熔断
    HALF_OPEN = "half_open" # 半开（探测恢复）


class CircuitOpenError(Exception):
    """
    熔断器开启异常。

    当熔断器处于 OPEN 状态时，所有通过 execute() 发起的调用都会被拒绝，
    抛出此异常。调用方可以捕获此异常实现降级逻辑（详见 query.py 的 _invoke_llm）。

    【为什么不直接返回 None 或默认值？】
    异常机制强制调用方"意识到"熔断正在发生。如果返回 None，
    调用方可能静默地将其当作正常响应处理，导致更隐蔽的 bug。
    显式抛出异常 = 显式处理。
    """
    pass


class CircuitBreaker:
    """
    三态熔断器。

    【生活中的类比：电路保险丝】
    家里的保险丝只有两态：通（正常）和断（熔断）。断了之后需要人手换新的。
    代码里的熔断器更智能——它有"自动试探恢复"能力（HALF_OPEN）。
    类比：保险丝烧了 → 等一会冷却 → 试着推上去 → 如果又烧了说明短路还在 → 继续断开。

    【三态转换图】

                  连续失败 >= failure_threshold
        CLOSED ──────────────────────────────→ OPEN
          ↑                                       │
          │           超过 recovery_timeout        │
          │        OPEN ──────────────────→ HALF_OPEN
          │                                       │
          │      试探成功                          │  试探失败
          └──── HALF_OPEN ───────────────────── CLOSED ────→ OPEN

    【参数说明】
    - failure_threshold: 连续失败多少次后触发熔断（默认 5）
    - recovery_timeout:  熔断后等待多久才能试探恢复（默认 60 秒）

    【为什么用"连续失败"而不是"时间窗口内失败率"？】
    连续失败计数是最简单的熔断策略，适合依赖方（如 LLM API）明确不可用的场景。
    如果需求更复杂（如偶发超时不应熔断），可以升级为滑动窗口计数。
    当前策略：简单、无状态、易理解。

    【线程安全】
    所有状态变更都通过 self._lock 保护。Python 的 GIL 只保证单字节码原子性，
    多步操作（如 state 读取 → 判断 → 写入）仍需要显式 Lock。
    """

    def __init__(
        self,
        name: str = "default",
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
    ):
        """
        初始化熔断器。

        参数：
          name              — 熔断器名称，用于日志区分（同一进程可有多个熔断器）
          failure_threshold — 连续失败阈值。例：5 表示连续 5 次失败后熔断
          recovery_timeout  — 恢复超时（秒）。熔断后等待这么久才进入 HALF_OPEN 试探

        初始状态：
          - state = CLOSED（正常，允许所有请求）
          - failure_count = 0（尚无失败记录）
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0.0
        self._lock = Lock()

    def _pre_call(self):
        """
        调用前检查（pre-call hook）。

        【执行逻辑】
        1. 如果当前状态不是 OPEN → 直接放行，不做任何事
        2. 如果当前状态是 OPEN：
           a. 检查距上次失败是否已过 recovery_timeout
              - 是 → 状态转为 HALF_OPEN，放行（试探恢复）
              - 否 → 抛出 CircuitOpenError，拒绝请求

        【为什么用异常而不是返回码？】
        熔断拒绝是一种"例外情况"，调用方必须主动处理。
        如果用 True/False 返回值，容易被忽略。
        异常 → 调用链上必须有人 catch，否则程序崩掉，这反而是好事（fail loud）。
        """
        with self._lock:
            if self.state == CircuitState.OPEN:
                if time.monotonic() - self.last_failure_time >= self.recovery_timeout:
                    self.state = CircuitState.HALF_OPEN
                    logger.info(f"[CIRCUIT:{self.name}] OPEN -> HALF_OPEN (recovery timeout)")
                else:
                    raise CircuitOpenError(
                        f"Circuit breaker '{self.name}' is OPEN. "
                        f"Retry after {self.recovery_timeout - (time.monotonic() - self.last_failure_time):.0f}s"
                    )

    def on_success(self):
        """
        调用成功回调（post-call success hook）。

        【执行逻辑】
        1. 如果当前状态是 HALF_OPEN → 说明试探请求成功，下游已恢复 → 记录日志
        2. 将状态重置为 CLOSED，失败计数清零

        【为什么成功了要重置状态？】
        熔断器关注的是"连续失败"模式。一次成功说明问题已经解决，
        应该给下游信任，重新全量放行。如果问题只是间歇性的，
        后续请求还会触发熔断——这是自愈 + 自适应。
        """
        with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                logger.info(f"[CIRCUIT:{self.name}] HALF_OPEN -> CLOSED")
            self.state = CircuitState.CLOSED
            self.failure_count = 0

    def on_failure(self):
        """
        调用失败回调（post-call failure hook）。

        【执行逻辑】
        1. failure_count += 1（累加连续失败次数）
        2. 记录失败时间戳（last_failure_time），用于后续恢复超时计算
        3. 如果连续失败次数 >= failure_threshold：
           - 如果还未处于 OPEN → 记录告警日志（CLOSED → OPEN）
           - 状态设为 OPEN（即使已经是 OPEN 也保持，确保 HALF_OPEN 失败后回到 OPEN）

        【为什么 HALF_OPEN 的试探失败也要重新 OPEN？】
        试探 = HALF_OPEN 下放行的第一个请求。如果它失败了，说明下游还没恢复。
        此时重新开闸（OPEN），重新计时 recovery_timeout，防止后续请求继续"硬怼"。
        这是一种保守策略：宁可多等一会，也不反复试探已确认未恢复的服务。
        """
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.monotonic()
            if self.failure_count >= self.failure_threshold:
                if self.state != CircuitState.OPEN:
                    logger.warning(
                        f"[CIRCUIT:{self.name}] CLOSED -> OPEN "
                        f"({self.failure_count} consecutive failures)"
                    )
                self.state = CircuitState.OPEN

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        在熔断器保护下执行函数。

        这是熔断器的唯一对外接口，所有需要保护的调用都通过此方法包装。

        【执行流程】
        ① _pre_call()    — 状态检查，OPEN 时拒绝，超时则转 HALF_OPEN
        ② func(*args)    — 执行实际业务逻辑
        ③ on_success()   — 成功 → 重置状态为 CLOSED
        ④ on_failure()   — 异常 → 累加失败计数，可能触发熔断

        【异常处理策略】
        - CircuitOpenError: 直接向上抛（这不是业务异常，是保护机制）
        - 其他 Exception:   调用 on_failure() 记录失败，然后重新抛出
          重新抛出很重要——让调用方知道请求失败了，自行决定重试或降级

        【典型用法】
            breaker = CircuitBreaker(name="llm", failure_threshold=5)
            try:
                result = breaker.execute(lambda: llm.invoke(messages))
            except CircuitOpenError:
                result = fallback_llm.invoke(messages)  # 降级
        """
        self._pre_call()
        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except CircuitOpenError:
            raise
        except Exception:
            self.on_failure()
            raise


# =========================================================================
# 全局实例
# =========================================================================

# 全局令牌桶（从配置读取，默认 100 QPS）
rate_limiter: Optional[TokenBucket] = None

# LLM 熔断器（全局单例）
# failure_threshold=5 : 连续 5 次调用 DeepSeek API 失败后触发熔断
# recovery_timeout=60 : 熔断 60 秒后自动进入 HALF_OPEN 试探恢复
llm_circuit_breaker = CircuitBreaker(name="llm", failure_threshold=5, recovery_timeout=60.0)


def init_rate_limiter(qps: int = 100):
    """
    初始化全局令牌桶。

    在应用启动时（lifespan）调用一次。
    设置 burst=qps 意味着允许瞬时突发到 QPS 上限，
    但长期平均不会超过 rate。

    【调用位置】
    routers/rag.py 中每个 RAG 端点入口检查 rate_limiter.consume()，
    令牌不足时直接返回 HTTP 200 + errCode="RATE_LIMITED"，
    前端可据此展示"系统繁忙"提示。
    """
    global rate_limiter
    rate_limiter = TokenBucket(rate=qps, burst=qps)
    logger.info(f"[RATE_LIMITER] Initialized: {qps} QPS")
