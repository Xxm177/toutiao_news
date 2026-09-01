# 头条新闻 App（前后端）

一个仿「今日头条」的新闻 App，前后端分离。

| 目录 | 说明 | 技术栈 |
|------|------|--------|
| `backend/` | 后端接口服务 | FastAPI + MySQL + Redis |
| `frontend/` | 移动端 H5 前端 | Vue 3 + Vite + Vant + Pinia |

## 项目结构

```
toutiao_news
├── backend/             # 后端（接口、数据库、缓存）
│   ├── main.py          # 入口，注册路由 + 启动后台任务
│   ├── config/          # 数据库 / Redis 连接配置
│   ├── cache/           # Redis 缓存（登录凭证、新闻缓存、浏览量）
│   ├── routers/         # 接口路由（news / users / favorite / history）
│   ├── crud/            # 数据库读写逻辑
│   ├── models/          # 数据库表结构（ORM 模型）
│   ├── schemas/         # 请求/响应数据模型
│   ├── utils/           # 工具（登录校验、密码加密）
│   └── docker-compose.yml  # 一键启动 MySQL + Redis
│
└── frontend/            # 前端（移动端页面）
    ├── src/views/       # 页面
    ├── src/components/  # 组件
    ├── src/router/      # 路由
    ├── src/store/       # 状态管理（Pinia）
    └── src/config/      # 接口地址、AI 问答配置
```

## 快速启动

### 1. 启动后端（依赖 MySQL 和 Redis）

```bash
cd backend

# 安装依赖
uv sync

# 配置数据库连接：复制 .env.example 为 .env，填自己的数据库密码

# 一键启动 MySQL 和 Redis（需要 Docker）
docker compose up -d

# 建表（首次运行一次即可）
python init_db.py

# 启动服务（默认端口 8000）
uvicorn main:app --host 127.0.0.1 --port 8000
```

> 详细说明见 [backend/README.md](backend/README.md)。

### 2. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 配置 AI 问答：复制 .env.example 为 .env，填自己的 DeepSeek API Key

# 启动开发服务器（默认端口 5173）
npm run dev
```

前端默认连接 `http://127.0.0.1:8000` 这个后端地址。

## 功能模块

| 模块 | 说明 |
|------|------|
| 新闻 | 分类、列表（分页）、详情（浏览量、相关新闻） |
| 用户 | 注册、登录、个人信息、改资料、改密码 |
| 收藏 | 添加、取消、列表、清空 |
| 历史 | 添加、列表、删除单条、清空 |
| AI 问答 | 基于 DeepSeek 的智能问答 |

## Redis 缓存优化

后端用 Redis 做了三处优化：

1. **登录凭证**：token 存 Redis，7 天自动过期，校验更快。
2. **新闻列表 / 分类**：5 分钟缓存，减少数据库查询压力。
3. **浏览量**：先记在 Redis，后台每 60 秒自动写回 MySQL，防止热点新闻压垮数据库。
