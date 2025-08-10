from sqlalchemy.orm import Session
from typing import List, Type
from app.models import Pet
from app.schemas import PetCreate, PetResponse
from app.services import posts
import time

def create_pet_for_user(db: Session, pet_data: PetCreate, user_id: int) -> Pet:
    image_url = None
    if pet_data.image:
        file_name = f"pet_{user_id}_{pet_data.name}_{int(time.time())}"
        image_url = posts.upload_file(pet_data.image, file_name)

    db_pet = Pet(
        **pet_data.model_dump(exclude={"image"}), # Excluimos 'image' para usar 'image_url'
        user_id=user_id,
        image=image_url
    )
    db.add(db_pet)
    db.commit()
    db.refresh(db_pet)
    return db_pet

def get_pets_for_user(db: Session, user_id: int) -> list[Type[Pet]]:
    return db.query(Pet).filter(Pet.user_id == user_id).order_by(Pet.created_at.desc()).all()