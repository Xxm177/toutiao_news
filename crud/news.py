from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from models.news import Category, News
from cache import news_cache

async def get_categories(db: AsyncSession, skip: int=0,limit: int=100):
    cached = await news_cache.get_categories_cache()
    if cached is not None:
        return cached
    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    categories = result.scalars().all()
    data = [news_cache.to_dict(c, news_cache.CATEGORY_FIELDS) for c in categories]
    await news_cache.set_categories_cache(data)
    return data

async def get_news_list(db: AsyncSession, categories_id: int, skip: int=0, limit: int=10):
    cached = await news_cache.get_news_list_cache(categories_id, skip, limit)
    if cached is not None:
        return cached
    stmt = select(News).where(News.category_id == categories_id).offset(skip).limit(limit)
    res = await db.execute(stmt)
    news_list = res.scalars().all()
    data = [news_cache.to_dict(n, news_cache.NEWS_FIELDS) for n in news_list]
    await news_cache.set_news_list_cache(categories_id, skip, limit, data)
    return data

async def get_news_count(db: AsyncSession, category_id: int):
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    res = await db.execute(stmt)
    return res.scalar_one()

async def get_news_detail(db: AsyncSession, news_id: int):
    stmt = select(News).where(News.id == news_id)
    res = await db.execute(stmt)
    return res.scalar_one_or_none()

async def increase_news_views(news_id: int) -> int:
    await news_cache.mark_dirty_view(news_id)
    return await news_cache.incr_views(news_id)

async def get_related_news(db: AsyncSession, news_id: int, category_id: int, limit: int = 5):
    stmt = select(News).where(News.id != news_id, News.category_id == category_id).order_by(News.views.desc(), News.publish_time.desc()).limit(limit)
    res = await db.execute(stmt)
    return res.scalars().all()