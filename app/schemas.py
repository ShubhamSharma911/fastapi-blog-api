from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


#userschema--------------------------------------------

class UserBase(BaseModel):
    email:EmailStr



class CreateUser(UserBase):
    password: str



class CreateUserResponse(UserBase):
    id:int
    created_at: datetime
    password:str
    class Config:
        from_attributes = True


class GetUsersResponse(UserBase):
    id: int
    created_at: datetime
    is_active: bool
    class Config:
        from_attributes = True



#posts-schema
class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    pass


class CreatePostResponse(PostBase):
    id:int
    created_at: datetime
    updated_at: datetime
    published: bool
    owner_id: int
    owner: CreateUserResponse
    class Config:
        from_attributes = True







#login schema----------------------------------------

class UserLogin(BaseModel):
    email: EmailStr
    password: str



class UserLoginResponse(BaseModel):
    id:int
    created_at: datetime
    email:EmailStr
    class Config:
        from_attributes = True



#Access Token-------------------------------------------



class Token(BaseModel):
    access_token: str
    token_type: str



class TokenData(BaseModel):
    id: Optional[int] = None
