from datetime import datetime
import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = "User"
    role: Optional[str] = "admin"
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = "User"
    role: Optional[str] = "admin"
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = True


class UserRegisterIn(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = "User"


class UserLoginIn(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = None


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None



class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

