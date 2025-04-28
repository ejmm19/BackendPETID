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
    type: str
    content: str

class PostCreate(PostBase):
    pass

class PostResponse(BaseModel):
    parent_id: int
    id: int
    type: str
    content: str
    created_at: datetime
    updated_at: datetime
    likes: int
    liked_by_user: bool

    class Config:
        from_attributes = True

class PostResponseFeed(BaseModel):
    parent_user_id: int
    parent_user: str
    id: int
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