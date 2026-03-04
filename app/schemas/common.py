from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel

T = TypeVar("T")


class PaginationParams(BaseModel):
    """分页参数"""
    page: int = 1
    size: int = 10

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


class Response(BaseModel, Generic[T]):
    """通用响应模型"""
    code: int = 200
    message: str = "success"
    data: Optional[T] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应模型"""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
