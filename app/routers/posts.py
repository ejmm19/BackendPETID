from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from fastapi.security import HTTPAuthorizationCredentials
from app.database import get_db
from app.schemas import PostCreate, PostResponse, PostResponseFeed, LostPetReportCreate, LostPetReportResponse, FeedItem
from app.services.posts import *
from app.utils.token import decode_token, security
from typing import List

router = APIRouter(prefix="/posts", tags=["Posts"])

@router.post("/")
def create_post_endpoint(post: PostCreate, db: Session = Depends(get_db), token: HTTPAuthorizationCredentials = Security(security)):
    user_id = decode_token(token.credentials)
    return create_post(post, db, user_id)

@router.get("/", response_model=List[PostResponse])
def get_all_posts_endpoint(db: Session = Depends(get_db), limit: int = 10, token: HTTPAuthorizationCredentials = Security(security)):
    user_id = decode_token(token.credentials)
    return get_all_posts(db, user_id, limit)

@router.get("/feed", response_model=List[FeedItem])
def get_all_posts_endpoint(db: Session = Depends(get_db), limit: int = 10, page: int = 1, token: HTTPAuthorizationCredentials = Security(security)):
    user_id = decode_token(token.credentials)
    return get_feed(db, user_id, limit, page)


@router.get("/posts/me", response_model=List[PostResponseFeed], summary="Obtener los posts del usuario actual")
def get_my_posts_endpoint(db: Session = Depends(get_db), token: HTTPAuthorizationCredentials = Security(security)):
    user_id = decode_token(token.credentials)
    return get_posts_by_user(db=db, user_id=user_id)

@router.put("/{post_id}", response_model=PostResponse)
def update_post_endpoint(post_id: int, post: PostCreate, db: Session = Depends(get_db), token: HTTPAuthorizationCredentials = Security(security)):
    user_id = decode_token(token.credentials)
    return update_post(post_id, post, db)

@router.delete("/{post_id}")
def delete_post_endpoint(post_id: int, db: Session = Depends(get_db), token: HTTPAuthorizationCredentials = Security(security)):
    user_id = decode_token(token.credentials)
    delete_post(post_id, db)
    return {"detail": "Post deleted"}

@router.post("/{post_id}/like")
def like_post_endpoint(post_id: int, db: Session = Depends(get_db), token: HTTPAuthorizationCredentials = Security(security)):
    user_id = decode_token(token.credentials)
    return toggle_like(user_id, post_id, db)

@router.post("/lost-pets")
def create_lost_pet_report(report: LostPetReportCreate, db: Session = Depends(get_db), token: HTTPAuthorizationCredentials = Security(security)):
    user_id = decode_token(token.credentials)
    return create_report(report, user_id, db)

@router.get("/report/{report_id}", response_model=LostPetReportResponse, summary="Obtener un reporte por su ID")
def get_single_report_endpoint(
    report_id: int,
    db: Session = Depends(get_db)
):
    return get_report_by_id(db=db, report_id=report_id)

@router.get("/lost-pets", response_model=List[LostPetReportResponse])
def get_lost_pet_reports(db: Session = Depends(get_db), limit: int = 10, token: HTTPAuthorizationCredentials = Security(security)):
    user_id = decode_token(token.credentials)
    return get_reports(db, user_id, limit)

@router.get("/{post_id}", response_model=PostResponse)
def get_post_endpoint(post_id: int, db: Session = Depends(get_db), token: HTTPAuthorizationCredentials = Security(security)):
    user_id = decode_token(token.credentials)
    return get_post(post_id, user_id, db)