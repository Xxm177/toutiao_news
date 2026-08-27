from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from models.news import Category, News

async def get_categories(db: AsyncSession, skip: int=0,limit: int=100):
    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_news_list(db: AsyncSession, categories_id: int, skip: int=0, limit: int=10):
    stmt = select(News).where(News.category_id == categories_id).offset(skip).limit(limit)
    res = await db.execute(stmt)
    return res.scalars().all()

async def get_news_count(db: AsyncSession, category_id: int):
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    res = await db.execute(stmt)
    return res.scalar_one()

async def get_news_detail(db: AsyncSession, news_id: int):
    stmt = select(News).where(News.id == news_id)
    res = await db.execute(stmt)
    return res.scalar_one_or_none()

async def increase_news_views(db: AsyncSession, news_id: int):
    stmt = update(News).where(News.id == news_id).values(views=News.views+1)
    res = await db.execute(stmt)
    await db.commit()
    return res.rowcount > 0

async def get_related_news(db: AsyncSession, news_id: int, category_id: int, limit: int = 5):
    stmt = select(News).where(News.id != news_id, News.category_id == category_id).order_by(News.views.desc(), News.publish_time.desc()).limit(limit)
    res = await db.execute(stmt)
    return res.scalars().all()