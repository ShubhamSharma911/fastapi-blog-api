from .. import models, utils
from .. import schemas,oauth2
from typing import List, Optional
from fastapi import FastAPI, HTTPException,APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import session
from starlette import status
from datetime import datetime, UTC
from ..database import get_db

router = APIRouter(
    prefix="/posts",
    tags=["post"]
)


@router.get("/", response_model=List[schemas.CreatePostResponse])
def get_posts(db: session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user), limit: int = 10, offset: int = 0, search: Optional[str] = "" ):

    posts = db.query(models.Post).filter(models.Post.is_deleted == False).filter(models.Post.content.contains(search)).limit(limit).offset(offset).all()
    return posts


@router.post("/", status_code= status.HTTP_201_CREATED, response_model = schemas.CreatePostResponse)
def create_posts(post: schemas.PostCreate, db: session = Depends(get_db), current_user = Depends(oauth2.get_current_user), limit:int = 10):

    print(current_user)
    #new_post = models.Post(**post.model_dump())
    new_post = models.Post(**post.model_dump(), owner_id=current_user.id)

    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("/{post_id}", status_code= status.HTTP_200_OK, response_model = schemas.CreatePostResponse)
def get_post(post_id: int, db: session = Depends(get_db),current_user = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).get(post_id)
    if post is None or post.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": f"Post with id {post_id} not found or has been deleted"}
        )
    return post

@router.delete("/{post_id}", status_code = status.HTTP_200_OK, )
def delete_post(post_id:int, db: session = Depends(get_db),current_user: models.User = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).get(post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the owner of the post")

    post.is_deleted = True
    db.commit()
    return {"message": f"Post with id {post_id} deleted successfully"}


@router.put("/{post_id}", status_code = status.HTTP_200_OK, response_model=schemas.CreatePostResponse)
def update_post(post_id: int, post: schemas.PostCreate, db: session = Depends(get_db),current_user: models.User = Depends(oauth2.get_current_user)):

    updated_post = db.query(models.Post).get(post_id)
    if updated_post is None or updated_post.is_deleted:
        raise HTTPException(status_code=404, detail="Post not found")
    if updated_post.owner_id !=current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the owner of the post")
    updated_post.content = post.content
    updated_post.title = post.title
    updated_post.updated_at = datetime.now(UTC)
    return updated_post