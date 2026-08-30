from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from models.history import History, News
from datetime import datetime

async def add_history(db: AsyncSession, user_id: int, news_id: int):
    query = select(History).where(History.user_id == user_id, History.news_id == news_id)
    res = await db.execute(query)
    existing_history = res.scalar_one_or_none()
    if existing_history:
        existing_history.view_time = datetime.now()
        await db.commit()
        await db.refresh(existing_history)
        return existing_history
    else:
        his = History(user_id = user_id, news_id = news_id)
        db.add(his)
        await db.commit()
        await db.refresh(his)
        return his

async def get_history_list(db: AsyncSession, user_id: int, offset: int = 0, limit: int = 10):
    stmt = select(History, News).join(News, History.news_id == News.id).where(History.user_id == user_id).order_by(History.view_time.desc()).offset(offset).limit(limit)
    res = await db.execute(stmt)
    rows = res.all()
    result = []
    for his, news in rows:
        result.append({
            "id": news.id,
            "title": news.title,
            "description": news.description,
            "image": news.image,
            "author": news.author,
            "publishTime": news.publish_time,
            "categoryId": news.category_id,
            "views": news.views,
            "viewTime": his.view_time
        })
    return result

async def get_total(db: AsyncSession, user_id: int):
    stmt = select(func.count(History.id)).where(History.user_id == user_id)
    res = await db.execute(stmt)
    return res.scalar_one()

async def delete_history(db: AsyncSession, user_id: int, news_id: int):
    stmt = delete(History).where(History.user_id == user_id, History.news_id == news_id)
    res = await db.execute(stmt)
    await db.commit()
    return res.rowcount>0

async def clear_history(db: AsyncSession,user_id: int):
    stmt = delete(History).where(History.user_id == user_id)
    res = await db.execute(stmt)
    await db.commit()
    return res.rowcount or 0