from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import Post
from app.schemas import PostCreate, PostResponse
from typing import List

def create_post(post: PostCreate, db: Session, user_id: int) -> PostResponse:
    db_post = Post(
        title=post.title,
        parent_id=user_id,
        type=post.type,
        content=post.content
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def get_all_posts(db: Session, limit: int = 10) -> List[PostResponse]:
    posts = db.query(Post).limit(limit).all()
    return posts

def get_post(post_id: int, db: Session) -> PostResponse:
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

def update_post(post_id: int, post: PostCreate, db: Session) -> PostResponse:
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    db_post.title = post.title
    db_post.type = post.type
    db_post.content = post.content
    db.commit()
    db.refresh(db_post)
    return db_post

def delete_post(post_id: int, db: Session):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(post)
    db.commit()