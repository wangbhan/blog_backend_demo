from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.article import Article, ArticleStatus
from app.models.user import User
from app.models.tag import Tag
from app.schemas.article import ArticleResponse
from app.schemas.user import UserResponse
from app.schemas.tag import TagResponse

router = APIRouter()


@router.get("")
async def search(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    type: Optional[str] = Query(None, description="搜索类型: article, user, tag"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """全局搜索"""
    results = {}

    # 搜索文章
    if type is None or type == "article":
        article_query = select(Article).options(
            selectinload(Article.author),
            selectinload(Article.tags)
        ).where(
            Article.status == ArticleStatus.PUBLISHED,
            or_(
                Article.title.contains(q),
                Article.content.contains(q),
                Article.summary.contains(q)
            )
        ).order_by(Article.created_at.desc())

        offset = (page - 1) * size
        result = await db.execute(article_query.offset(offset).limit(size))
        articles = result.scalars().all()

        results["articles"] = [ArticleResponse.model_validate(a) for a in articles]

    # 搜索用户
    if type is None or type == "user":
        user_query = select(User).where(
            or_(
                User.username.contains(q),
                User.bio.contains(q)
            )
        ).order_by(User.created_at.desc())

        offset = (page - 1) * size
        result = await db.execute(user_query.offset(offset).limit(size))
        users = result.scalars().all()

        results["users"] = [UserResponse.model_validate(u) for u in users]

    # 搜索标签
    if type is None or type == "tag":
        tag_query = select(Tag).where(Tag.name.contains(q))

        result = await db.execute(tag_query)
        tags = result.scalars().all()

        results["tags"] = [TagResponse.model_validate(t) for t in tags]

    return results
