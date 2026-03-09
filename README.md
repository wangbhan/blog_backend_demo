# 个人博客系统

一个基于 FastAPI + Next.js 构建的现代化个人博客系统。

服务已经部署到：https://blog-frontend-demo.vercel.app/

## 技术栈

### 后端

- FastAPI - 高性能异步框架
- SQLAlchemy 2.0 - ORM
- SQLite/Turso - 数据库
- JWT - 认证

## 项目结构

```
web_blog/
├── backend/          # FastAPI 后端
    ├── app/
    │   ├── api/      # API 路由
    │   ├── models/   # 数据库模型
    │   ├── schemas/  # Pydantic 模型
    │   └── utils/    # 工具函数
    └── uploads/      # 上传文件目录
```

## 快速开始

### 后端启动

```bash
cd backend

# 创建虚拟环境并安装依赖
uv venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

uv sync

# 启动服务
uv run uvicorn app.main:app --reload --port 8000
```

后端 API 文档: http://localhost:8000/docs

## 功能特性

- [x] 用户注册/登录
- [x] 文章 CRUD
- [x] Markdown 编辑器
- [x] 分类和标签
- [x] 评论系统（支持嵌套）
- [x] 全局搜索
- [x] 用户个人主页
- [x] 个人设置
- [x] 图片上传

## API 接口

### 认证

- POST /api/auth/register - 注册
- POST /api/auth/login - 登录
- GET /api/auth/me - 获取当前用户
- PUT /api/auth/me - 更新用户信息

### 文章

- GET /api/articles - 文章列表
- GET /api/articles/{id} - 文章详情
- POST /api/articles - 创建文章
- PUT /api/articles/{id} - 更新文章
- DELETE /api/articles/{id} - 删除文章
- POST /api/articles/{id}/like - 点赞

### 分类

- GET /api/categories - 分类列表
- POST /api/categories - 创建分类
- PUT /api/categories/{id} - 更新分类
- DELETE /api/categories/{id} - 删除分类

### 标签

- GET /api/tags - 标签列表
- POST /api/tags - 创建标签
- DELETE /api/tags/{id} - 删除标签

### 评论

- GET /api/comments/article/{article_id} - 获取评论
- POST /api/comments - 发表评论
- DELETE /api/comments/{id} - 删除评论

### 搜索

- GET /api/search - 全局搜索

### 上传

- POST /api/upload/image - 上传图片

## 部署

### 后端部署

可部署到 Railway、Fly.io 或 Render 等平台。

## 环境变量

### 后端 (.env)

```
DATABASE_URL=sqlite+aiosqlite:///./blog.db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://localhost:3000
```

## License

MIT