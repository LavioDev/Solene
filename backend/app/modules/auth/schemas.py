from datetime import datetime
from typing import Any, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


class PermissionBase(BaseModel):
    code: str
    name: str
    module: str
    description: Optional[str] = None


class PermissionCreate(PermissionBase):
    pass


class PermissionOut(PermissionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AssignPermissionsPayload(BaseModel):
    permission_ids: List[uuid.UUID] = Field(default_factory=list)


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = "User"
    role: Optional[str] = "user"
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = "User"
    role: Optional[str] = "user"
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = True
    permission_ids: Optional[List[uuid.UUID]] = None


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
    permission_ids: Optional[List[uuid.UUID]] = None


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    permissions: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator("permissions", mode="before")
    @classmethod
    def parse_permissions(cls, v: Any) -> List[str]:
        if not v:
            return []
        res = []
        for item in v:
            if hasattr(item, "code"):
                res.append(item.code)
            elif isinstance(item, str):
                res.append(item)
            elif isinstance(item, dict) and "code" in item:
                res.append(item["code"])
        return res

    @model_validator(mode="after")
    def populate_admin_wildcard(self) -> "UserOut":
        if self.role == "admin" and not self.permissions:
            self.permissions = ["*"]
        return self


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
