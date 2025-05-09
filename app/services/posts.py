from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import Post, Like, User, LostPetReport, UserPostType, PostImage
from app.schemas import PostCreate, PostResponse, PostResponseFeed
from typing import List
from app.utils.uploadfile import upload_file_to_s3_base64
import time

def create_post(post: PostCreate, db: Session, user_id: int) -> dict:
    try:
        # Crear el post
        db_post = Post(
            parent_id=user_id,
            type=post.type,
            content=post.content
        )
        db.add(db_post)
        db.commit()
        db.refresh(db_post)

        # Validar si post.image no está vacío
        if post.image:
            # Subir la imagen a S3
            file_name = f"post_{user_id}_{int(time.time())}"
            image_url = upload_file(post.image, file_name)

            # Guardar en la tabla post_images
            post_image = PostImage(
                post_id=db_post.id,
                image_url=image_url
            )
            db.add(post_image)
            db.commit()

        return {"message": "Post created successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

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
        if post.type == "image":
            post_image = db.query(PostImage).filter(PostImage.post_id == post.id).first()
            post_image_url = post_image.image_url if post_image else ""
        else:
            post_image_url = ""
        post_responses.append(PostResponseFeed(
            parent_user_id=parent_user.id,
            parent_user=parent_user.first_name + " " + parent_user.last_name,
            id=post.id,
            type=post.type,
            content=post.content,
            image=post_image_url,
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

def create_report(report, user_id: int, db: Session) -> dict:
    try:
        file_base64 = report.image
        file_name = f"{user_id}_{report.pet_name}_{int(time.time())}"
        report.image = upload_file(file_base64, file_name)

        db_report = LostPetReport(**report.dict())
        db.add(db_report)
        db.commit()
        db.refresh(db_report)

        user_post_type = UserPostType(
            user_id=user_id,
            post_id=db_report.id,
            post_type="lost_pet_report"
        )
        db.add(user_post_type)
        db.commit()

        return {"message": "Report created successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

def upload_file(file_base64, file_name: str) -> str:
    if file_base64.startswith("data:image"):
        image_format = file_base64.split(";")[0].split("/")[1]  # Obtiene el formato (e.g., png, jpg)
        file_base64 = file_base64.split(",")[1]  # Elimina el prefijo
    else:
        raise ValueError("El contenido Base64 no tiene un prefijo válido.")

    # Construir la clave del archivo con el formato
    s3_key = f"carpeta_en_s3/{file_name}.{image_format}"

    # Subir el archivo a S3
    upload_file_to_s3_base64(file_base64, s3_key)
    # Retornar la URL del archivo subido
    image_url = "https://petid001.s3.us-east-1.amazonaws.com/"+s3_key
    return image_url

def get_reports(db: Session, user_id: int, limit = 10) -> List[LostPetReport]:
    reports = db.query(LostPetReport).order_by(LostPetReport.created_at.desc()).limit(limit).all()
    report_responses = []
    for report in reports:
        report_responses.append(report)
    return report_responses