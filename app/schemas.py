from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import List, Union, Dict, Any
import json

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
    parent_user_profile_image: dict
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
    last_seen_location: Dict[str, float]
    additional_details: str
    contact_phone: str
    contact_email: EmailStr

class LostPetReportCreate(LostPetReportBase):
    @field_validator("last_seen_location", mode='before')
    @classmethod
    def parse_location(cls, v: Any) -> Any:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                raise ValueError("El string de ubicación no es un JSON válido")
        return v

class LostPetReportResponse(LostPetReportBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class FeedItem(BaseModel):
    item_type: str  # 'post' o 'lost_pet_report'
    data: Union[PostResponseFeed, LostPetReportResponse]

class MediaProfileBase(BaseModel):
    user_id: int
    media_type: str
    image_base64: str

class CommentCreate(BaseModel):
    content: str

class CommentAuthorResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    media: dict = {}

class CommentResponse(BaseModel):
    id: int
    content: str
    created_at: datetime
    author: CommentAuthorResponse

    class Config:
        from_attributes = True

class CommentUpdate(BaseModel):
    content: str

class PetBase(BaseModel):
    name: str
    species: str
    breed: str
    color: str
    image: str
    gender: str
    birth_date: datetime

class PetCreate(PetBase):
    pass

class PetResponse(PetBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True