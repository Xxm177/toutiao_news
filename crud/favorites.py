from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from models.favorites import Favorite
from models.news import News

async def check(db: AsyncSession, user_id: int, news_id: int):
    stmt = select(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    res = await db.execute(stmt)
    return res.scalar_one_or_none() is not None

async def add_favorite(db: AsyncSession, user_id: int, news_id: int):
    if await check(db, user_id, news_id):
        return None
    favorite = Favorite(user_id=user_id, news_id=news_id)
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite

async def remove(db: AsyncSession, user_id: int, news_id: int):
    stmt = delete(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    res = await db.execute(stmt)
    await db.commit()
    return res.rowcount>0

async def get_favorite_list(db: AsyncSession, user_id: int):
    stmt = (
        select(Favorite, News)
        .join(News, Favorite.news_id == News.id)
        .where(Favorite.user_id == user_id)
        .order_by(Favorite.created_at.desc())
    )
    res = await db.execute(stmt)
    rows = res.all()
    result = []
    for fav, news in rows:
        result.append({
            "id": news.id,
            "title": news.title,
            "image": news.image,
            "author": news.author,
            "publishTime": news.publish_time,
            "favoriteTime": fav.created_at,
        })
    return result

async def clear_favorites(db: AsyncSession, user_id: int):
    stmt = delete(Favorite).where(Favorite.user_id == user_id)
    res = await db.execute(stmt)
    await db.commit()
    return res.rowcount