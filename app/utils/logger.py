import sys
import os
from loguru import logger

from app.config import settings


def setup_logger():
    """配置 loguru 日志系统"""
    # 移除默认的 handler
    logger.remove()

    # 检测是否在 Vercel 环境
    is_vercel = os.environ.get("VERCEL") is not None

    # 日志格式
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    # 文件日志格式（不带颜色）
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss} | "
        "{level: <8} | "
        "{name}:{function}:{line} - "
        "{message}"
    )

    # 控制台输出
    # Vercel 环境不支持 multiprocessing，禁用 enqueue
    logger.add(
        sys.stdout,
        format=log_format,
        level=settings.LOG_LEVEL,
        colorize=True,
        enqueue=False,  # Vercel 不支持
    )

    # 文件输出（仅本地环境）
    if not is_vercel:
        # 确保日志目录存在
        log_dir = os.path.dirname(settings.LOG_FILE)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 文件输出（按日期轮转，保留7天）
        logger.add(
            settings.LOG_FILE,
            format=file_format,
            level=settings.LOG_LEVEL,
            rotation="00:00",  # 每天轮转
            retention="7 days",  # 保留7天
            compression="zip",  # 压缩旧日志
            encoding="utf-8",
            enqueue=False,  # Vercel 不支持
        )

    logger.info(f"日志系统初始化完成 | 级别: {settings.LOG_LEVEL}")

    return logger
