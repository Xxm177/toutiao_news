from pydantic import BaseModel

class UserRequest(BaseModel):
    username: str
    password: str

class UserUpdateRequest(BaseModel):
    nickname: str = None
    avatar: str = None
    gender: str = None
    bio: str = None
    phone: str = None

class Password(BaseModel):
    oldPassword: str
    newPassword: str