from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db
from app.api import api_router
from app.utils.logger import setup_logger, logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 初始化日志系统
    setup_logger()
    logger.info(f"启动 {settings.APP_NAME}")
    # 启动时初始化数据库
    await init_db()
    logger.info("数据库初始化完成")
    yield
    # 关闭时清理资源
    logger.info("应用关闭")


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    description="现代化个人博客系统API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录（用于图片上传）
import os

# Vercel 环境使用 /tmp 目录，本地使用 uploads 目录
upload_dir = "/tmp/uploads" if os.environ.get("VERCEL") else "uploads"

try:
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")
except OSError:
    # Vercel 只读文件系统时跳过静态文件挂载
    pass

# 注册路由
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": f"欢迎来到{settings.APP_NAME}",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
