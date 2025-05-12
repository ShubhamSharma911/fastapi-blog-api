from .. import models,schemas
from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import session
from starlette import status
from datetime import datetime, UTC
from typing import List
from .. import utils
from ..database import get_db

router = APIRouter(
    prefix="/users",
    tags=["user"]
)

@router.post("", status_code= status.HTTP_201_CREATED, response_model=schemas.CreateUserResponse)
def create_user(user: schemas.CreateUser, db: session = Depends(get_db)):
    hashed_password = utils.hash_password(user.password)

    new_user = models.User(**user.model_dump())
    new_user.password = hashed_password
    new_user.created_at = datetime.now(UTC)
    new_user.updated_at = datetime.now(UTC)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("", status_code= status.HTTP_200_OK, response_model=List[schemas.CreateUserResponse])
def get_users(db: session = Depends(get_db)):
    users = db.query(models.User).filter(models.User.is_deleted == False).all()
    print(users)
    return users


@router.delete("/{user_id}",status_code= status.HTTP_200_OK)
def delete_users(user_id:int, db: session = Depends(get_db)):
    user = db.query(models.User).get(user_id)
    if user is None or user.is_deleted:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_deleted = True
    return "deleted"


@router.get("/{user_id}",status_code= status.HTTP_200_OK)
def get_user_by_id(user_id: int, db: session = Depends(get_db), response_model=schemas.CreateUserResponse):
    user = db.query(models.User).get(user_id)
    if user is None or  user.is_deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return user
