import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# 加载 .env 文件里的配置（数据库密码等），避免密码写死在代码里
load_dotenv()

# 数据库连接地址从环境变量读取
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+aiomysql://root:news123456@localhost:3306/news_app?charset=utf8mb4",
)

async_engine = create_async_engine(
    DATABASE_URL,
    echo = True,
    pool_size = 10,
    max_overflow = 20
)

AsyncSessionLocal = async_sessionmaker(
    bind = async_engine,
    class_ = AsyncSession,
    expire_on_commit=False
)

async def get_db():
      async with AsyncSessionLocal() as db:
          yield db