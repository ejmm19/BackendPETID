from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import Post, Like, User, LostPetReport, UserPostType, PostImage, MediaProfile, Comment
from app.schemas import PostCreate, PostResponse, PostResponseFeed, FeedItem, LostPetReportResponse, CommentCreate, \
    CommentResponse, CommentAuthorResponse
from typing import List, Optional
from app.utils.uploadfile import upload_file_to_s3_base64
import time
import json
from datetime import timezone

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

def get_media_profile(user_id: int, db: Session) -> dict:
    media_profile = db.query(MediaProfile).filter(
        MediaProfile.user_id == user_id,
        MediaProfile.media_type == "profile"
    ).first()
    if media_profile:
        return {"url": media_profile.image_url}
    return {}



def get_feed(db: Session, user_id: int, limit: int, page: int) -> List[FeedItem]:
    skip = (page - 1) * limit
    posts_query = db.query(Post).order_by(Post.created_at.desc()).offset(skip).limit(limit).all()
    #reports_query = db.query(LostPetReport).order_by(LostPetReport.created_at.desc()).offset(skip).limit(limit).all()

    feed_items = []

    for post in posts_query:
        likes_count = get_likes(post.id, db)
        liked_by_user = is_liked_by_user(user_id, post.id, db)
        parent_user = db.query(User).filter(User.id == post.parent_id).first()

        post_image_url = ""
        if post.type == "image":
            post_image = db.query(PostImage).filter(PostImage.post_id == post.id).first()
            if post_image:
                post_image_url = post_image.image_url

        post_data = PostResponseFeed(
            parent_user_id=parent_user.id,
            parent_user=f"{parent_user.first_name} {parent_user.last_name}",
            parent_user_profile_image= get_media_profile(parent_user.id, db),
            id=post.id,
            type=post.type,
            content=post.content,
            image=post_image_url,
            created_at=post.created_at.replace(tzinfo=timezone.utc),
            updated_at=post.updated_at.replace(tzinfo=timezone.utc),
            likes=likes_count,
            liked_by_user=liked_by_user
        )
        feed_items.append(FeedItem(item_type="post", data=post_data))

    reports_query = db.query(LostPetReport).order_by(LostPetReport.created_at.desc()).limit(limit).all()

    for report in reports_query:
        import json
        last_seen_data = report.last_seen_location
        if isinstance(last_seen_data, str):
            try:
                last_seen_data = json.loads(last_seen_data)
            except json.JSONDecodeError:
                last_seen_data = {}

        report_data = LostPetReportResponse(
            id=report.id,
            pet_name=report.pet_name,
            species=report.species,
            breed=report.breed,
            color=report.color,
            image=report.image,
            gender=report.gender,
            lost_date=report.lost_date,
            last_seen_location=last_seen_data,
            additional_details=report.additional_details,
            contact_phone=report.contact_phone,
            contact_email=report.contact_email,
            created_at=report.created_at.replace(tzinfo=timezone.utc),
            updated_at=report.updated_at.replace(tzinfo=timezone.utc)
        )
        feed_items.append(FeedItem(item_type="lost_pet_report", data=report_data))

    feed_items.sort(key=lambda item: item.data.created_at, reverse=True)

    return feed_items


def get_posts_by_user(db: Session, user_id: int) -> List[PostResponseFeed]:
    user_posts_query = db.query(Post).filter(Post.parent_id == user_id).order_by(Post.created_at.desc()).all()

    post_responses = []

    if not user_posts_query:
        return post_responses

    parent_user = db.query(User).filter(User.id == user_id).first()

    for post in user_posts_query:
        likes_count = get_likes(post.id, db)
        liked_by_user = is_liked_by_user(user_id, post.id, db)

        post_image_url = ""
        if post.type == "image":
            post_image = db.query(PostImage).filter(PostImage.post_id == post.id).first()
            if post_image:
                post_image_url = post_image.image_url

        post_data = PostResponseFeed(
            parent_user_id=parent_user.id,
            parent_user=f"{parent_user.first_name} {parent_user.last_name}",
            parent_user_profile_image={},
            id=post.id,
            type=post.type,
            content=post.content,
            image=post_image_url,
            created_at=post.created_at.replace(tzinfo=timezone.utc),
            updated_at=post.updated_at.replace(tzinfo=timezone.utc),
            likes=likes_count,
            liked_by_user=liked_by_user
        )
        post_responses.append(post_data)

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
    existing_like = db.query(Like).filter(
        Like.user_id == user_id,
        Like.post_id == post_id
    ).first()

    if existing_like:
        db.delete(existing_like)
        db.commit()
        return {"message": "Like removed successfully"}
    else:
        new_like = Like(user_id=user_id, post_id=post_id)
        db.add(new_like)
        db.commit()
        return {"message": "Like added successfully"}

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


def get_report_by_id(db: Session, report_id: int) -> LostPetReportResponse:
    report = db.query(LostPetReport).filter(LostPetReport.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")

    last_seen_data = report.last_seen_location
    if isinstance(last_seen_data, str):
        try:
            last_seen_data = json.loads(last_seen_data)
        except json.JSONDecodeError:
            last_seen_data = {}  # o algún valor por defecto

    return LostPetReportResponse(
        id=report.id,
        pet_name=report.pet_name,
        species=report.species,
        breed=report.breed,
        color=report.color,
        image=report.image,
        gender=report.gender,
        lost_date=report.lost_date,
        last_seen_location=last_seen_data,
        additional_details=report.additional_details,
        contact_phone=report.contact_phone,
        contact_email=report.contact_email,
        created_at=report.created_at.replace(tzinfo=timezone.utc),
        updated_at=report.updated_at.replace(tzinfo=timezone.utc)
    )

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

def create_comment(db: Session, post_id: int, user_id: int, comment: CommentCreate) -> CommentResponse:
    # Verificamos que el post al que se comenta existe
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post no encontrado")

    # Creamos la instancia del comentario
    db_comment = Comment(
        content=comment.content,
        post_id=post_id,
        user_id=user_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)

    # Obtenemos los datos del autor para la respuesta
    author = db.query(User).filter(User.id == user_id).first()
    author_media = get_media_profile(user_id, db) # Reutilizamos tu lógica de media

    # Devolvemos el comentario recién creado con el formato correcto
    return CommentResponse(
        id=db_comment.id,
        content=db_comment.content,
        created_at=db_comment.created_at,
        author=CommentAuthorResponse(
            id=author.id,
            first_name=author.first_name,
            last_name=author.last_name,
            media=author_media
        )
    )


def get_comments_for_post(db: Session, post_id: int) -> List[CommentResponse]:
    # Hacemos un join para obtener los datos del comentario y del autor en una sola consulta
    results = db.query(Comment, User).join(User, Comment.user_id == User.id).filter(
        Comment.post_id == post_id).order_by(Comment.created_at.asc()).all()

    response = []
    for comment, author in results:
        author_media = get_media_profile(author.id, db)
        response.append(
            CommentResponse(
                id=comment.id,
                content=comment.content,
                created_at=comment.created_at,
                author=CommentAuthorResponse(
                    id=author.id,
                    first_name=author.first_name,
                    last_name=author.last_name,
                    media=author_media
                )
            )
        )
    return response


def delete_comment(db: Session, comment_id: int, user_id: int):
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not db_comment:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")

    # ¡Importante! Verificamos que el usuario que intenta borrar es el autor del comentario
    if db_comment.user_id != user_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para borrar este comentario")

    db.delete(db_comment)
    db.commit()
    return {"message": "Comentario eliminado exitosamente"}