from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.user import User
from app.models.article import Article, ArticleStatus
from app.schemas.user import UserResponse
from app.schemas.article import ArticleResponse, ArticleListResponse

router = APIRouter()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """获取用户信息"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return UserResponse.model_validate(user)


@router.get("/{user_id}/articles", response_model=ArticleListResponse)
async def get_user_articles(
    user_id: int,
    page: int = 1,
    size: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """获取用户的文章列表"""
    # 检查用户是否存在
    result = await db.execute(select(User).where(User.id == user_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="用户不存在")

    # 查询文章
    query = select(Article).where(
        Article.author_id == user_id,
        Article.status == ArticleStatus.PUBLISHED
    ).order_by(Article.created_at.desc())

    # 计算总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 分页
    offset = (page - 1) * size
    result = await db.execute(query.offset(offset).limit(size))
    articles = result.scalars().all()

    return ArticleListResponse(
        items=[ArticleResponse.model_validate(a) for a in articles],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )
