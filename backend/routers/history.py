from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from utils.auth import get_current_user
from config.db_conf import get_db
from models.users import User
from schemas.history import HistoryAddRequest
from crud.history import add_history, get_history_list, get_total, delete_history, clear_history

router = APIRouter(prefix="/api/history", tags=["history"])

@router.post("/add")
async def add(data: HistoryAddRequest, user: User=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    res = await add_history(db, user.id, data.news_id)
    return {
    "code": 200,
    "message": "添加成功",
    "data": {
        "id": res.id,
        "userId": res.user_id,
        "newsId": res.news_id,
        "viewTime": res.view_time
    }
    }

@router.get("/list")
async def get_list(page: int=1, pagesize: int=Query(10,alias="pageSize",le=100), user: User=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    res = await get_history_list(db, user.id, page, pagesize)
    offset = (page - 1) * pagesize
    total = await get_total(db, user.id)
    has_more = (offset+len(res))<total
    return {
        "code": 200,
        "message": "获取历史浏览列表成功",
        "data": {
            "list": res,
            "total": total,
            "hasMore": has_more
        }
    }

@router.delete("/delete/{history_id}")
async def to_delete(history_id: int, user: User=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    res = await delete_history(db, user.id, history_id)
    if not res:
        raise HTTPException(status_code=404, detail="未找到该记录")
    return {
    "code": 200,
    "message": "删除成功",
    "data": ""
    }

@router.delete("/clear")
async def clear(user: User=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    res = await clear_history(db, user.id)
    return{
    "code": 200,
    "message": "清空成功",
    "data": ""
    }