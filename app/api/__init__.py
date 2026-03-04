from fastapi import APIRouter
from app.api import auth, users, articles, categories, tags, comments, search, upload

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(articles.router, prefix="/articles", tags=["文章"])
api_router.include_router(categories.router, prefix="/categories", tags=["分类"])
api_router.include_router(tags.router, prefix="/tags", tags=["标签"])
api_router.include_router(comments.router, prefix="/comments", tags=["评论"])
api_router.include_router(search.router, prefix="/search", tags=["搜索"])
api_router.include_router(upload.router, prefix="/upload", tags=["上传"])
