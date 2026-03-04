from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CategoryBase(BaseModel):
    """分类基础模型"""
    name: str
    slug: str
    description: Optional[str] = None


class CategoryCreate(BaseModel):
    """分类创建模型"""
    name: str
    description: Optional[str] = None


class CategoryUpdate(BaseModel):
    """分类更新模型"""
    name: Optional[str] = None
    description: Optional[str] = None


class CategoryResponse(CategoryBase):
    """分类响应模型"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
