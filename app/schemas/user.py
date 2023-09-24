from datetime import datetime

from db.models import UserRole
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field(min_length=2, max_length=30)
    email: EmailStr


class UserSignUp(UserBase):
    username: str = Field(min_length=2, max_length=30)
    email: EmailStr
    password: str = Field(min_length=6, max_length=14)


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
    success: bool = True

    class ConfigDict:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    success: bool
