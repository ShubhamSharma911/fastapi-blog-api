from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import session
from starlette import status
from datetime import datetime, UTC
from . import models, schemas
from app.database import engine, SessionLocal

models.Base.metadata.drop_all(bind=engine)  # Drops all tables defined in models
models.Base.metadata.create_all(bind=engine)  # Recreates all tables

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/posts", response_model=List[schemas.CreatePostResponse])
def get_posts(db: session = Depends(get_db)):

    posts = db.query(models.Post).filter(models.Post.is_deleted == False).all()
    return posts


@app.post("/posts", status_code= status.HTTP_201_CREATED, response_model = schemas.CreatePostResponse)
def create_posts(post: schemas.PostCreate, db: session = Depends(get_db)):
    new_post = models.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@app.get("/posts/{post_id}", status_code= status.HTTP_200_OK, response_model = schemas.CreatePostResponse)
def get_post(post_id: int, db: session = Depends(get_db)):
    post = db.query(models.Post).get(post_id)
    if post is None or post.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": f"Post with id {post_id} not found or has been deleted"}
        )
    return post

@app.delete("/posts/{post_id}", status_code = status.HTTP_200_OK)
def delete_post(post_id:int, db: session = Depends(get_db)):
    post = db.query(models.Post).get(post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    post.is_deleted = True
    db.commit()
    return {"message": f"Post with id {post_id} deleted successfully"}


@app.put("/posts/{post_id}", status_code = status.HTTP_200_OK, response_model=schemas.CreatePostResponse)
def update_post(post_id: int, post: schemas.PostCreate, db: session = Depends(get_db)):
    updated_post = db.query(models.Post).get(post_id)
    if updated_post is None or updated_post.is_deleted:
        raise HTTPException(status_code=404, detail="Post not found")
    updated_post.content = post.content
    updated_post.title = post.title
    updated_post.updated_at = datetime.now(UTC)
    return updated_post


#Users------------

@app.post("/users", status_code= status.HTTP_201_CREATED, response_model=schemas.CreateUserResponse)
def create_user(user: schemas.CreateUser, db: session = Depends(get_db)):
    new_user = models.User(**user.model_dump())
    new_user.created_at = datetime.now(UTC)
    new_user.updated_at = datetime.now(UTC)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/users", status_code= status.HTTP_200_OK, response_model=List[schemas.CreateUserResponse])
def get_users(db: session = Depends(get_db)):
    users = db.query(models.User).all()
    return users


@app.delete("/users/{user_id}",status_code= status.HTTP_200_OK)
def delete_users(user_id:int, db: session = Depends(get_db)):
    user = db.query(models.User).get(user_id)
    if user is None or user.is_deleted:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_deleted = True
    return "deleted"

