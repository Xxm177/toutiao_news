import uuid
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from models.users import User, UserToken
from schemas.users import UserRequest, UserUpdateRequest
from utils import security
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
    expires_at = datetime.now() + timedelta(days=7)
    stmt = select(UserToken).where(UserToken.user_id == user_id)
    res = await db.execute(stmt)
    user_token = res.scalar_one_or_none()
    if user_token:
        user_token.token = token
        user_token.expires_at = expires_at
        await db.commit()
    else:
        user_token = UserToken(user_id=user_id, token=token, expires_at=expires_at)
        db.add(user_token)
        await db.commit()
    return token

async def user_login(db: AsyncSession, user_data: UserRequest):
    user = await get_user_by_username(db, user_data.username)
    if not user:
        return None
    if not security.verify_pwd(user_data.password, user.password):
        return None
    return user

async def get_user_by_token(db: AsyncSession, token: str):
    user = select(UserToken).where(UserToken.token == token)
    res = await db.execute(user)
    db_token = res.scalar_one_or_none()
    if not db_token or db_token.expires_at < datetime.now():
        return None
    query = select(User).where(User.id == db_token.user_id)
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
