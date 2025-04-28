from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import Post, Like, User
from app.schemas import PostCreate, PostResponse, PostResponseFeed
from typing import List

def create_post(post: PostCreate, db: Session, user_id: int) -> dict:
    db_post = Post(
        parent_id=user_id,
        type=post.type,
        content=post.content
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return {"message": "Post created successfully"}

def get_all_posts(db: Session, user_id, limit: int = 10) -> List[PostResponse]:
    posts = db.query(Post).limit(limit).all()
    post_responses = []
    for post in posts:
        likes_count = get_likes(post.id, db)
        liked_by_user = is_liked_by_user(user_id, post.id, db)
        post_responses.append(PostResponse(
            parent_id=post.parent_id,
            id=post.id,
            type=post.type,
            content=post.content,
            created_at=post.created_at,
            updated_at=post.updated_at,
            likes=likes_count,
            liked_by_user=liked_by_user
        ))
    return post_responses

def get_feed(db: Session, user_id, limit: int = 10) -> List[PostResponseFeed]:
    posts = db.query(Post).order_by(Post.created_at.desc()).limit(limit).all()
    post_responses = []
    for post in posts:
        likes_count = get_likes(post.id, db)
        liked_by_user = is_liked_by_user(user_id, post.id, db)
        parent_user = db.query(User).filter(User.id == post.parent_id).first()
        post_responses.append(PostResponseFeed(
            parent_user_id=parent_user.id,
            parent_user=parent_user.first_name + " " + parent_user.last_name,
            id=post.id,
            type=post.type,
            content=post.content,
            created_at=post.created_at,
            updated_at=post.updated_at,
            likes=likes_count,
            liked_by_user=liked_by_user
        ))
    return post_responses

def get_post(post_id: int, user_id, db: Session) -> PostResponse:
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Contar los likes del post
    likes_count = get_likes(post_id, db)
    liked_by_user = is_liked_by_user(user_id, post_id, db)

    return PostResponse(
        parent_id=post.parent_id,
        id=post.id,
        type=post.type,
        content=post.content,
        created_at=post.created_at,
        updated_at=post.updated_at,
        likes=likes_count,
        liked_by_user=liked_by_user
    )

def update_post(post_id: int, post: PostCreate, db: Session) -> PostResponse:
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
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

## logic for like post
def toggle_like(user_id: int, post_id: int, db: Session) -> dict:
    like = Like(user_id=user_id, post_id=post_id)
    db.add(like)
    db.commit()
    db.refresh(like)
    return {"message": "Like saved successfully"}

def get_likes(post_id: int, db: Session) -> int:
    likes_count = db.query(Like).filter(Like.post_id == post_id).count()
    return likes_count

def is_liked_by_user(user_id: int, post_id: int, db: Session) -> bool:
    existing_like = db.query(Like).filter(Like.user_id == user_id, Like.post_id == post_id).first()
    return True if existing_like else False