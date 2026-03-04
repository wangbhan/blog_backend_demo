from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.comment import Comment
from app.models.article import Article
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse
from app.utils.dependencies import get_current_active_user

router = APIRouter()


@router.get("/article/{article_id}", response_model=list[CommentResponse])
async def get_article_comments(
    article_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取文章的评论列表"""
    # 检查文章是否存在
    result = await db.execute(select(Article).where(Article.id == article_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="文章不存在")

    # 获取评论
    query = select(Comment).options(
        selectinload(Comment.user)
    ).where(
        Comment.article_id == article_id
    ).order_by(Comment.created_at.desc())

    result = await db.execute(query)
    comments = result.scalars().all()

    return [CommentResponse.model_validate(c) for c in comments]


@router.post("", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """发表评论"""
    # 检查文章是否存在
    result = await db.execute(select(Article).where(Article.id == comment_data.article_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="文章不存在")

    # 如果是回复，检查父评论是否存在
    if comment_data.parent_id:
        result = await db.execute(
            select(Comment).where(Comment.id == comment_data.parent_id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="回复的评论不存在")

    comment = Comment(
        content=comment_data.content,
        article_id=comment_data.article_id,
        user_id=current_user.id,
        parent_id=comment_data.parent_id
    )

    db.add(comment)
    await db.commit()
    await db.refresh(comment)

    # 重新查询以加载用户信息
    result = await db.execute(
        select(Comment)
        .options(selectinload(Comment.user))
        .where(Comment.id == comment.id)
    )
    comment = result.scalar_one()

    return CommentResponse.model_validate(comment)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """删除评论"""
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")

    # 检查权限：只能删除自己的评论
    if comment.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权限删除此评论")

    await db.delete(comment)
    await db.commit()
