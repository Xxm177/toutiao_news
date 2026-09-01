import uuid
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from models.users import User
from schemas.users import UserRequest, UserUpdateRequest
from utils import security
from cache import token_cache
async def get_user_by_username(db: AsyncSession, username: str):
    stmt = select(User).where(User.username == username)
    res = await db.execute(stmt)
    return res.scalar_one_or_none()

async def create_user(db: AsyncSession, user_data: UserRequest):
    hashed_password = security.get_hash_pwd(user_data.password)
    user = User(username = user_data.username, password = hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def get_token(db: AsyncSession, user_id: int):
    token = str(uuid.uuid4())
    await token_cache.set_token(token, user_id)
    return token

async def user_login(db: AsyncSession, user_data: UserRequest):
    user = await get_user_by_username(db, user_data.username)
    if not user:
        return None
    if not security.verify_pwd(user_data.password, user.password):
        return None
    return user

async def get_user_by_token(db: AsyncSession, token: str):
    user_id = await token_cache.get_user_id_by_token(token)
    if user_id is None:
        return None
    query = select(User).where(User.id == user_id)
    res = await db.execute(query)
    return res.scalar_one_or_none()

async def update_uesr_info(db: AsyncSession, username:str, user_data: UserUpdateRequest):
    query = update(User).where(User.username == username).values(**user_data.model_dump(exclude_unset=True, exclude_none=True))
    res = await db.execute(query)
    await db.commit()
    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="未更新成功")
    updated = await get_user_by_username(db, username)
    return updated

async def update_user_password(db: AsyncSession, user: User, oldpassword: str, newpassword: str):
    if not security.verify_pwd(oldpassword, user.password):
        return False
    new_hash_password = security.get_hash_pwd(newpassword)
    user.password = new_hash_password
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return True
