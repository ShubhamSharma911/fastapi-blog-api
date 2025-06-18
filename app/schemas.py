from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, conint, ConfigDict, Field


# User schema
class UserBase(BaseModel):
    email: EmailStr


class CreateUser(UserBase):
    password: str


class CreateUserResponse(UserBase):
    id: int
    created_at: datetime
    password: str
    model_config = ConfigDict(from_attributes=True)


class GetUsersResponse(UserBase):
    id: int
    created_at: datetime
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str



# Post schema
class PostBase(BaseModel):
    title: str
    content: str


class PostCreate(PostBase):
    pass


class CreatePostResponse(PostBase):
    id: int
    created_at: datetime
    updated_at: datetime
    published: bool
    owner_id: int
    owner: CreateUserResponse
    model_config = ConfigDict(from_attributes=True)


class GetallAllPostsResponse(BaseModel):
    Post: CreatePostResponse
    votes: int
    model_config = ConfigDict(from_attributes=True)


# Login schema
class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserLoginResponse(BaseModel):
    id: int
    created_at: datetime
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


# Access Token
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[int] = None


# Vote
class Vote(BaseModel):
    post_id: int
    dir: conint(ge=0, le=1)


#resumes

class ResumeUploadResponse(BaseModel):
    message: str
    filename: Optional[str] = None
    uploaded_at: Optional[datetime] = None

# Payment

class CreateOrderRequest(BaseModel):
    user_id: int
    amount: float = Field(gt=0, description="Amount in rupees")

class CreateOrderResponse(BaseModel):
    order_id: str
    amount: int
    currency: str