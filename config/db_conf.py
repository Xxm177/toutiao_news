from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

DATABASE_URL = "mysql+aiomysql://root:CHANGE_ME@localhost:3306/news_app?charset=utf8mb4"

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