from datetime import date, datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, model_validator


class UserPartnerSummary(BaseModel):
    id: UUID
    email: str
    full_name: str
    avatar_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CoupleBase(BaseModel):
    start_date: date
    nickname: Optional[str] = None
    status: str = "active"
    cover_url: Optional[str] = None


class CoupleCreate(BaseModel):
    user1_id: Optional[UUID] = None
    user2_id: UUID
    start_date: date
    nickname: Optional[str] = None
    status: str = "active"
    cover_url: Optional[str] = None

    @model_validator(mode="after")
    def validate_different_users(self) -> "CoupleCreate":
        if self.user1_id and self.user1_id == self.user2_id:
            raise ValueError("user1_id and user2_id must be different")
        return self


class CoupleUpdate(BaseModel):
    user1_id: Optional[UUID] = None
    user2_id: Optional[UUID] = None
    start_date: Optional[date] = None
    nickname: Optional[str] = None
    status: Optional[str] = None
    cover_url: Optional[str] = None


class CoupleOut(BaseModel):
    id: UUID
    user1_id: UUID
    user2_id: UUID
    start_date: date
    nickname: Optional[str] = None
    status: str
    cover_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    user1: Optional[UserPartnerSummary] = None
    user2: Optional[UserPartnerSummary] = None
    days_together: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def compute_days_together(self) -> "CoupleOut":
        if self.start_date:
            today = date.today()
            delta = (today - self.start_date).days
            self.days_together = max(0, delta)
        return self


class CoupleInvitationCreateResponse(BaseModel):
    id: UUID
    inviter_id: UUID
    code: str
    status: str
    expires_at: datetime
    created_at: datetime
    invite_url: Optional[str] = None
    inviter: Optional[UserPartnerSummary] = None

    model_config = ConfigDict(from_attributes=True)


class CoupleInvitationInfoResponse(BaseModel):
    code: str
    status: str
    is_valid: bool
    expires_at: datetime
    inviter: Optional[UserPartnerSummary] = None
    error_reason: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CoupleInvitationAcceptPayload(BaseModel):
    code: str
    start_date: date
    nickname: Optional[str] = None
    cover_url: Optional[str] = None

