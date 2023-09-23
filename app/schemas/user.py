# from dataclasses import dataclass
from datetime import datetime

# from fastapi import Form

from db.models import UserRole
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field(min_length=2, max_length=30)
    email: EmailStr

#
# @dataclass
# class UserSignUp:
#     username: str = Form(...)  # Field(min_length=2, max_length=30)
#     email: Form(...)  # EmailStr
#     password: str = Form(...)  # Field(min_length=6, max_length=14)


class UserSignUp(UserBase):
    # username: str = Field(min_length=2, max_length=30)
    # email: str # EmailStr
    password: str = Field(min_length=6, max_length=14)
    # grant_type: str = "password"
    # scope: str = "default"
    # client_id: str = "your-client-id"
    # client_secret: str = "your-client-secret"

#
# class UserAny:
#     ...


class UserUpdate(BaseModel):
    username: None | str = Field(min_length=2, max_length=30, default=None)
    password: None | str = Field(min_length=6, max_length=30, default=None)


class UserFullUpdate(UserUpdate):
    email: None | EmailStr = None
    avatar: None | str
    role: UserRole = UserRole.USER
    confirmed: bool = Field(default=True)
    status_active: bool = Field(default=True)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: str | None
    role: UserRole
    status_active: bool

    class ConfigDict:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
