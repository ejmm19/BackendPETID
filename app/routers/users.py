from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse, UserCreateResponse, UserLogin
import bcrypt
from app.services.users import create_user, get_user, authenticate_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserCreateResponse)
def create_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    response = create_user(user, db)
    return response

@router.get("/{user_id}", response_model=UserResponse)
def get_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    return get_user(user_id, db)

@router.post("/login", response_model=UserCreateResponse)
def login_user_endpoint(user: UserLogin, db: Session = Depends(get_db)):
    response = authenticate_user(user.email, user.password, db)
    return response