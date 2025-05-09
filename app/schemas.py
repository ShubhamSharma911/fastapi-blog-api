from datetime import datetime

from pydantic import BaseModel, EmailStr


#posts-schema
class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    pass


class CreatePostResponse(PostBase):
    created_at: datetime
    updated_at: datetime
    published: bool

    class Config:
        orm_mode = True

#userschema
class UserBase(BaseModel):
    email:EmailStr

class CreateUser(UserBase):
    password: str

class CreateUserResponse(UserBase):
    id:int
    created_at: datetime
    class Config:
        orm_mode = True

class GetUsersResponse(UserBase):
    id: int
    created_at: datetime
    is_active: bool
    class Config:
        orm_mode = True





