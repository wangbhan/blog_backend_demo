from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

from app.schemas.user import UserResponse


class CommentBase(BaseModel):
    """评论基础模型"""
    content: str


class CommentCreate(CommentBase):
    """评论创建模型"""
    article_id: int
    parent_id: Optional[int] = None


class CommentResponse(CommentBase):
    """评论响应模型"""
    id: int
    article_id: int
    user_id: int
    parent_id: Optional[int] = None
    user: UserResponse
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CommentTreeResponse(CommentBase):
    """评论树响应模型（包含嵌套回复）"""
    id: int
    article_id: int
    user_id: int
    parent_id: Optional[int] = None
    user: UserResponse
    replies: List["CommentTreeResponse"] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
