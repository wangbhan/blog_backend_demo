from datetime import datetime
from pydantic import BaseModel


class TagBase(BaseModel):
    """标签基础模型"""
    name: str
    slug: str


class TagCreate(BaseModel):
    """标签创建模型"""
    name: str


class TagResponse(TagBase):
    """标签响应模型"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
