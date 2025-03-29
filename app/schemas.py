from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(BaseModel):
    first_name: str
    last_name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True

class UserCreateResponse(BaseModel):
    user_data: UserResponse
    access_token: str

class PostBase(BaseModel):
    title: str
    type: str
    content: str

class PostCreate(PostBase):
    pass

class PostResponse(BaseModel):
    parent_id: int
    id: int
    title: str
    type: str
    content: str
    created_at: datetime
    updated_at: datetime
    likes: int
    liked_by_user: bool

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: str
    password: str