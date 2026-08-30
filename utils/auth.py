from fastapi import Header, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


from config.db_conf import get_db
from crud import users
async def get_current_user(authorization: str=Header(...,alias="Authorization"), db: AsyncSession=Depends(get_db)):
    token = authorization.replace("Bearer ","")
    user = await users.get_user_by_token(db, token)
    if not user:
        return HTTPException(status_code=404,detail="未匹配用户")
    return user
