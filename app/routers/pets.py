from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from fastapi.security import HTTPAuthorizationCredentials
from app.database import get_db
from app.utils.token import decode_token, security
from typing import List

from app.schemas import PetCreate, PetResponse
from app.services.pets import create_pet_for_user, get_pets_for_user

router = APIRouter(prefix="/pets", tags=["Pets"])

@router.post("/", response_model=PetResponse, summary="Crear una nueva mascota para el usuario actual")
def create_pet_endpoint(
    pet: PetCreate,
    db: Session = Depends(get_db),
    token: HTTPAuthorizationCredentials = Security(security)
):
    user_id = decode_token(token.credentials)
    return create_pet_for_user(db=db, pet_data=pet, user_id=user_id)

@router.get("/user/{user_id}", response_model=List[PetResponse], summary="Obtener las mascotas de un usuario específico")
def get_user_pets_endpoint(
    user_id: int,
    db: Session = Depends(get_db)
):
    return get_pets_for_user(db=db, user_id=user_id)