from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import User, MediaProfile
from app.schemas import UserCreate, UserCreateResponse
import bcrypt
from app.utils.token import generate_token

def create_user(user: UserCreate, db: Session) -> UserCreateResponse:
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    db_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password_hash=hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Generate the token
    token = generate_token(db_user.id)

    return {"user_data": db_user, "access_token": token}

def get_user(user_id: int, db: Session) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    media_profiles = get_media_profile(user_id, db)

    user_data = {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "media": media_profiles,
        "created_at": user.created_at
    }
    return user_data

def authenticate_user(email: str, password: str, db: Session) -> dict:
    user = db.query(User).filter(User.email == email).first()
    if not user or not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = generate_token(user.id)
    user_data = {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "media": {},
        "email": user.email,
        "created_at": user.created_at
    }
    return {"access_token": token, "user_data": user_data}

def add_media_profile(user_id: int, media_type: str, image_base64: str, db: Session) -> dict:
    existing_profile = db.query(MediaProfile).filter(MediaProfile.user_id == user_id, MediaProfile.media_type == media_type).first()
    image_url = 'https://placehold.co/100x100'
    if existing_profile:
        existing_profile.image_url = image_url
    else:
        new_profile = MediaProfile(user_id=user_id, media_type=media_type, image_url=image_url)
        db.add(new_profile)
    db.commit()
    return {"message": "Media profile updated successfully"}

def get_media_profile(user_id: int, db: Session) -> dict:
    media_profiles = db.query(MediaProfile).filter(MediaProfile.user_id == user_id).all()
    media = {profile.media_type: profile.image_url for profile in media_profiles}
    return media