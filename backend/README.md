# 头条新闻 App 后端

一个仿「今日头条」的新闻 App 后端接口服务，用 FastAPI 编写，配套前端在 `../frontend`。

## 技术栈

| 分类 | 技术 |
|------|------|
| Web 框架 | FastAPI（异步） |
| 数据库 | MySQL（SQLAlchemy 2.0 异步 + aiomysql） |
| 缓存 | Redis（redis.asyncio 异步） |
| 密码加密 | bcrypt（passlib） |
| 语言 / 包管理 | Python 3.14 / uv |

## 项目结构

```
backend
├── main.py              # 入口，注册路由 + 启动后台任务
├── config/
│   ├── db_conf.py       # MySQL 数据库连接配置
│   └── cache_conf.py    # Redis 连接配置
├── cache/
│   ├── token_cache.py   # 登录凭证的存入/读取/删除
│   └── news_cache.py    # 新闻列表、分类缓存 + 浏览量计数
├── routers/             # 接口路由（news / users / favorite / history）
├── crud/                # 数据库读写逻辑
├── models/              # 数据库表结构（ORM 模型）
├── schemas/             # 请求/响应的数据模型
└── utils/               # 工具（登录校验、密码加密）
```

## 启动前准备

需要 MySQL 和 Redis 两个后台服务。最简单的办法是用项目里准备好的 docker-compose 一键启动：

```bash
# 在项目根目录执行，会同时启动 MySQL 和 Redis
docker compose up -d
```

> 不想用 Docker 的话，也可以自己装 MySQL 和 Redis，只要 MySQL 跑在 `localhost:3306`、Redis 跑在 `localhost:6379` 即可。

## 启动后端

```bash
# 1. 安装依赖
uv sync

# 2. 配置数据库连接（首次）
#    复制 .env.example 为 .env，把里面的密码改成你自己的数据库密码

# 3. 建表（首次运行一次即可）
python init_db.py

# 4. 启动服务（默认端口 8000）
uvicorn main:app --host 127.0.0.1 --port 8000
```

启动成功后，访问 `http://127.0.0.1:8000/` 能看到 `{"message":"API running"}`。

前端（`../frontend`）默认就是连 `http://127.0.0.1:8000` 这个地址。

## 功能模块

| 模块 | 前缀 | 主要接口 |
|------|------|---------|
| 新闻 | `/api/news` | 分类、列表（分页）、详情（含浏览量、相关新闻） |
| 用户 | `/api/user` | 注册、登录、个人信息、改资料、改密码 |
| 收藏 | `/api/favorite` | 是否已收藏、添加、取消、列表、清空 |
| 历史 | `/api/history` | 添加、列表、删除单条、清空 |

## Redis 缓存说明

后端用 Redis 做了三处优化：

1. **登录凭证**：登录后的 token 存 Redis，7 天自动过期，校验更快。
2. **新闻列表 / 分类**：加了 5 分钟缓存，减少数据库查询压力。
3. **浏览量**：先记在 Redis，后台每 60 秒自动写回 MySQL，防止热点新闻压垮数据库。

## 备注

- 密码用 bcrypt 加密后存数据库，不存明文。
- 接口返回统一格式：`{ code, message, data }`。
- 需要登录的接口（收藏、历史等）要在请求头带 `Authorization: Bearer <token>`。
