from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

from app.schemas.user import UserResponse
from app.schemas.category import CategoryResponse
from app.schemas.tag import TagResponse
from app.schemas.comment import CommentTreeResponse


class ArticleBase(BaseModel):
    """文章基础模型"""
    title: str
    content: str
    summary: Optional[str] = None
    cover_image: Optional[str] = None
    category_id: Optional[int] = None
    tag_ids: List[int] = []


class ArticleCreate(ArticleBase):
    """文章创建模型"""
    status: str = "draft"


class ArticleUpdate(BaseModel):
    """文章更新模型"""
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    cover_image: Optional[str] = None
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None
    status: Optional[str] = None


class ArticleResponse(ArticleBase):
    """文章响应模型"""
    id: int
    view_count: int = 0
    like_count: int = 0
    status: str
    author_id: int
    category_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ArticleListResponse(BaseModel):
    """文章列表响应"""
    items: List[ArticleResponse]
    total: int
    page: int
    size: int
    pages: int


class ArticleDetailResponse(BaseModel):
    """文章详情响应"""
    id: int
    title: str
    content: str
    summary: Optional[str] = None
    cover_image: Optional[str] = None
    view_count: int = 0
    like_count: int = 0
    status: str
    author: UserResponse
    category: Optional[CategoryResponse] = None
    tags: List[TagResponse] = []
    comments: List[CommentTreeResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
