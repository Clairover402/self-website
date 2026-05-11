"""
日志配置模块

统一配置 Python logging 模块，提供结构化日志输出。
在应用启动时调用 setup_logging() 初始化全局日志配置。

日志级别：
- DEBUG 模式：控制台输出 DEBUG 及以上级别
- 非 DEBUG 模式：控制台输出 INFO 及以上级别

日志格式：
- 包含时间戳、模块名、日志级别和消息内容
- 便于 grep 和日志分析工具解析
"""

import logging
import sys


def setup_logging(debug: bool = False) -> None:
    """
    初始化全局日志配置

    参数：
        debug: 是否开启 DEBUG 级别日志（通常读取 settings.DEBUG 配置）

    配置内容：
    - 将日志输出到标准错误流（stderr），不干扰标准输出
    - 格式：[时间] [模块] [级别] 消息内容
    - 第三方库（如 sqlalchemy、uvicorn）的日志级别设为 WARNING，
      减少噪音，避免淹没应用自身的日志
    """
    level = logging.DEBUG if debug else logging.INFO

    # 根 logger 配置
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # 清除已有的 handler，避免重复添加（uvicorn reload 时可能触发）
    if root_logger.handlers:
        root_logger.handlers.clear()

    # 创建控制台 handler，输出到 stderr
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(level)

    # 日志格式：[2026-05-11 14:30:00] [routers.blog] [WARNING] 博客未找到
    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 抑制第三方库的 DEBUG/INFO 日志，减少控制台噪音
    # sqlalchemy.engine 在 echo=True 时也会输出日志
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    # 应用启动日志
    logging.getLogger(__name__).info("日志系统已初始化 | debug=%s", debug)
