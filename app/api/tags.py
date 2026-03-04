from slugify import slugify
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.tag import Tag
from app.models.user import User
from app.schemas.tag import TagCreate, TagResponse
from app.utils.dependencies import get_current_active_user

router = APIRouter()


@router.get("", response_model=list[TagResponse])
async def list_tags(db: AsyncSession = Depends(get_db)):
    """获取标签列表"""
    result = await db.execute(select(Tag).order_by(Tag.created_at))
    tags = result.scalars().all()
    return [TagResponse.model_validate(t) for t in tags]


@router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_data: TagCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """创建标签（需要登录）"""
    # 生成slug
    slug = slugify(tag_data.name)

    # 检查是否已存在
    result = await db.execute(select(Tag).where(Tag.slug == slug))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="标签已存在")

    tag = Tag(name=tag_data.name, slug=slug)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)

    return TagResponse.model_validate(tag)


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """删除标签"""
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()

    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    await db.delete(tag)
    await db.commit()
