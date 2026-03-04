from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User
from app.models.article import Article, ArticleStatus
from app.models.category import Category
from app.models.tag import Tag
from app.schemas.article import (
    ArticleCreate,
    ArticleUpdate,
    ArticleResponse,
    ArticleListResponse,
    ArticleDetailResponse
)
from app.utils.dependencies import get_current_active_user, get_optional_user

router = APIRouter()


@router.get("", response_model=ArticleListResponse)
async def list_articles(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    category_id: Optional[int] = None,
    tag_id: Optional[int] = None,
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """获取文章列表"""
    query = select(Article).options(
        selectinload(Article.author),
        selectinload(Article.category),
        selectinload(Article.tags)
    )

    # 筛选条件
    if category_id:
        query = query.where(Article.category_id == category_id)

    if tag_id:
        query = query.where(Article.tags.any(Tag.id == tag_id))

    if keyword:
        query = query.where(
            or_(
                Article.title.contains(keyword),
                Article.content.contains(keyword)
            )
        )

    # 状态筛选：非登录用户只能看已发布的
    if status and current_user and current_user.is_superuser:
        query = query.where(Article.status == ArticleStatus(status))
    else:
        query = query.where(Article.status == ArticleStatus.PUBLISHED)

    # 排序
    query = query.order_by(Article.created_at.desc())

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


@router.get("/{article_id}", response_model=ArticleDetailResponse)
async def get_article(
    article_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取文章详情"""
    query = select(Article).options(
        selectinload(Article.author),
        selectinload(Article.category),
        selectinload(Article.tags),
        selectinload(Article.comments).selectinload(Article.comments.property.mapper.class_.user)
    ).where(Article.id == article_id)

    result = await db.execute(query)
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    if article.status != ArticleStatus.PUBLISHED:
        raise HTTPException(status_code=404, detail="文章不存在")

    # 增加浏览量
    article.view_count += 1
    await db.commit()

    # 构建评论树
    comments_tree = build_comment_tree(article.comments)

    return ArticleDetailResponse(
        id=article.id,
        title=article.title,
        content=article.content,
        summary=article.summary,
        cover_image=article.cover_image,
        view_count=article.view_count,
        like_count=article.like_count,
        status=article.status.value,
        author=article.author,
        category=article.category,
        tags=article.tags,
        comments=comments_tree,
        created_at=article.created_at,
        updated_at=article.updated_at
    )


def build_comment_tree(comments):
    """构建评论树"""
    from app.schemas.comment import CommentTreeResponse
    from app.schemas.user import UserResponse

    comment_map = {}
    root_comments = []

    # 先将所有评论放入map
    for comment in comments:
        comment_map[comment.id] = CommentTreeResponse(
            id=comment.id,
            content=comment.content,
            article_id=comment.article_id,
            user_id=comment.user_id,
            parent_id=comment.parent_id,
            user=UserResponse.model_validate(comment.user),
            replies=[],
            created_at=comment.created_at,
            updated_at=comment.updated_at
        )

    # 构建树形结构
    for comment in comments:
        if comment.parent_id is None:
            root_comments.append(comment_map[comment.id])
        else:
            parent = comment_map.get(comment.parent_id)
            if parent:
                parent.replies.append(comment_map[comment.id])

    return root_comments


@router.post("", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
async def create_article(
    article_data: ArticleCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """创建文章"""
    # 创建文章
    article = Article(
        title=article_data.title,
        content=article_data.content,
        summary=article_data.summary,
        cover_image=article_data.cover_image,
        category_id=article_data.category_id,
        author_id=current_user.id,
        status=ArticleStatus(article_data.status) if article_data.status else ArticleStatus.DRAFT
    )

    # 添加标签
    if article_data.tag_ids:
        result = await db.execute(select(Tag).where(Tag.id.in_(article_data.tag_ids)))
        article.tags = list(result.scalars().all())

    db.add(article)
    await db.commit()
    await db.refresh(article)

    return ArticleResponse.model_validate(article)


@router.put("/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: int,
    article_data: ArticleUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新文章"""
    result = await db.execute(
        select(Article).where(Article.id == article_id).options(selectinload(Article.tags))
    )
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    # 检查权限
    if article.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权限修改此文章")

    # 更新字段
    update_data = article_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if field == "tag_ids" and value is not None:
            result = await db.execute(select(Tag).where(Tag.id.in_(value)))
            article.tags = list(result.scalars().all())
        elif field == "status" and value is not None:
            article.status = ArticleStatus(value)
        elif field not in ["tag_ids", "status"]:
            setattr(article, field, value)

    await db.commit()
    await db.refresh(article)

    return ArticleResponse.model_validate(article)


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    article_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """删除文章"""
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    # 检查权限
    if article.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权限删除此文章")

    await db.delete(article)
    await db.commit()


@router.post("/{article_id}/like", response_model=ArticleResponse)
async def like_article(
    article_id: int,
    db: AsyncSession = Depends(get_db)
):
    """点赞文章"""
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    article.like_count += 1
    await db.commit()
    await db.refresh(article)

    return ArticleResponse.model_validate(article)
