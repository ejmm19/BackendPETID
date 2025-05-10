from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    media: dict
    created_at: datetime

    class Config:
        from_attributes = True

class UserCreateResponse(BaseModel):
    user_data: UserResponse
    access_token: str

class PostBase(BaseModel):
    type: str
    image: str
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
    image: str
    created_at: datetime
    updated_at: datetime
    likes: int
    liked_by_user: bool

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: str
    password: str

class LostPetReportBase(BaseModel):
    pet_name: str
    species: str
    breed: str
    color: str
    image: str
    gender: str
    lost_date: datetime
    last_seen_location: str
    additional_details: str
    contact_phone: str
    contact_email: EmailStr

class LostPetReportCreate(LostPetReportBase):
    pass

class LostPetReportResponse(LostPetReportBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class MediaProfileBase(BaseModel):
    user_id: int
    media_type: str
    image_base64: str