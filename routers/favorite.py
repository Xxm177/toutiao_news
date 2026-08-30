from fastapi import APIRouter, Depends, Query, HTTPException
from config.db_conf import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from models.users import User
from utils.auth import get_current_user
from crud.favorites import check, add_favorite, remove, get_favorite_list, get_favorite_count, clear_favorites
from schemas.favorites import FavoriteAdd

router = APIRouter(prefix="/api/favorite",tags=["favorite"])

@router.get("/check")
async def check_my_favorite(news_id: int=Query(..., alias="newsId"), user: User=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    get_news = await check(db, user.id, news_id)
    return {
    "code": 200,
    "message": "success",
    "data": {
        "isFavorite": get_news
    }
    }

@router.post("/add")
async def add_favorite_news(favorite_data: FavoriteAdd, user: User=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    res = await add_favorite(db, user.id, favorite_data.newsId)
    if not res:
        raise HTTPException(status_code=400, detail="已经收藏过了")
    return {
    "code": 200,
    "message": "收藏成功",
    "data": {
        "id": res.id,
        "userId": res.user_id,
        "newsId": res.news_id,
        "createTime": res.created_at
    }
    }

@router.delete("/remove")
async def remove_favorite(news_id: int=Query(...,alias="newsId"), user: User=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    res = await remove(db, user.id, news_id)
    if not res:
        raise HTTPException(status_code=404, detail="收藏不存在")
    return {
    "code": 200,
    "message": "取消收藏成功",
    "data": ""
    }

@router.get("/list")
async def favorite_list(page: int = 1, page_size: int = Query(10, alias="pageSize", le=100), user: User=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    offset = (page - 1) * page_size
    fav_list = await get_favorite_list(db, user.id, offset, page_size)
    total = await get_favorite_count(db, user.id)
    has_more = (offset + len(fav_list)) < total
    return {
    "code": 200,
    "message": "获取收藏列表成功",
    "data": {
        "list": fav_list,
        "total": total,
        "hasMore": has_more
    }
    }

@router.delete("/clear")
async def clear_favorite(user: User=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    await clear_favorites(db, user.id)
    return {
    "code": 200,
    "message": "清空收藏成功",
    "data": ""
    }

