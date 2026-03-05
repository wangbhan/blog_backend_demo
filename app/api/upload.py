import os
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.utils.dependencies import get_current_active_user

router = APIRouter()

# 上传目录 - Vercel 环境使用 /tmp 目录
UPLOAD_DIR = "/tmp/uploads" if os.environ.get("VERCEL") else "uploads"


def ensure_upload_dir():
    """确保上传目录存在"""
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
):
    """上传图片"""
    # 检查文件类型
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="不支持的文件类型，仅支持 JPG, PNG, GIF, WEBP"
        )

    # 检查文件大小 (5MB)
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="文件大小不能超过 5MB")

    # 生成文件名
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}.{ext}"

    # 确保目录存在
    ensure_upload_dir()

    # 保存文件
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(content)

    # 返回URL
    return {
        "url": f"/uploads/{filename}",
        "filename": filename
    }
