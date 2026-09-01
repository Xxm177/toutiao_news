import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import update

from routers import news, users, favorite, history
from config.db_conf import AsyncSessionLocal
from models.news import News
from cache import news_cache


async def sync_views_loop():
    """后台任务：每 60 秒把 Redis 里的浏览量增量写回数据库一次"""
    while True:
        await asyncio.sleep(60)
        try:
            dirty = await news_cache.get_dirty_views()
            if not dirty:
                continue
            async with AsyncSessionLocal() as db:
                for news_id in dirty:
                    nid = int(news_id)
                    increment = await news_cache.get_views_increment(nid)
                    if increment:
                        await db.execute(
                            update(News).where(News.id == nid).values(views=News.views + increment)
                        )
                    await news_cache.clear_view(nid)
                await db.commit()
        except Exception as e:
            print(f"浏览量写回数据库失败: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(sync_views_loop())
    yield
    task.cancel()


app = FastAPI(title="头条", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)
app.include_router(history.router)


@app.get("/")
async def hello():
    return {"message": "API running"}
