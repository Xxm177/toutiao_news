from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_db
from schemas.users import UserRequest, UserUpdateRequest, Password
from crud import users
from utils import auth
from models.users import User

router = APIRouter(prefix="/api/user",tags=["users"])

@router.post("/register")
async def register(user_data: UserRequest, db: AsyncSession=Depends(get_db)):
    existing = await users.get_user_by_username(db, user_data.username)
    if existing:
        raise HTTPException(status_code=404, detail="该用户已存在")
    user = await users.create_user(db, user_data)
    token = await users.get_token(db, user.id)
    return {
    "code": 200,
    "message": "注册成功",
    "data": {
        "token": token,
        "userInfo": {
        "id": user.id,
        "username": user.username,
        "bio": user.bio,
        "avatar": user.avatar
        }
    }
    }

@router.post("/login")
async def login(user_data: UserRequest, db: AsyncSession=Depends(get_db)):
    user = await users.user_login(db, user_data)
    if not user:
        raise HTTPException(status_code=404, detail="未找到用户")
    token = await users.get_token(db, user.id)
    return {
    "code": 200,
    "message": "登录成功",
    "data": {
        "token": token,
        "userInfo": {
        "id": user.id,
        "username": user.username,
        "nickname": user.nickname,
        "avatar": user.avatar,
        "bio": user.bio
        }
    }
    }

@router.get("/info")
async def get_user_info(user: User=Depends(auth.get_current_user)):
    return {
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "username": user.username,
        "nickname": user.nickname,
        "avatar": user.avatar,
        "gender": user.gender,
        "bio": user.bio
    }
    }

@router.put("/update")
async def update(user_data: UserUpdateRequest, user: User=Depends(auth.get_current_user), db: AsyncSession=Depends(get_db)):
    user_update = await users.update_uesr_info(db, user.username, user_data)
    return {
    "code": 200,
    "message": "更新成功",
    "data": {
        "id": user.id,
        "username": user.username,
        "nickname": user_update.nickname,
        "avatar": user_update.avatar,
        "gender": user_update.gender,
        "bio": user_update.bio
    }
    }

@router.put("/password")
async def update_password(user_data: Password, user: User=Depends(auth.get_current_user), db: AsyncSession=Depends(get_db)):
    user = await users.update_user_password(db, user, user_data.oldPassword, user_data.newPassword)
    if not user:
        raise HTTPException(status_code=404, detail="更改密码失败")
    return {
    "code": 200,
    "message": "密码修改成功",
    "data": ""
    }