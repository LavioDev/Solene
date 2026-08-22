from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, model_validator


class TaskBase(BaseModel):
    title: str
    content: Optional[str] = None
    is_completed: bool = False
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    priority: str = "medium"


class TaskCreate(TaskBase):
    @model_validator(mode="after")
    def validate_time_range(self) -> "TaskCreate":
        if self.start_time and self.end_time and self.end_time < self.start_time:
            raise ValueError("end_time must be greater than or equal to start_time")
        return self


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_completed: Optional[bool] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    priority: Optional[str] = None

    @model_validator(mode="after")
    def validate_time_range(self) -> "TaskUpdate":
        if self.start_time and self.end_time and self.end_time < self.start_time:
            raise ValueError("end_time must be greater than or equal to start_time")
        return self


class TaskToggleStatus(BaseModel):
    is_completed: Optional[bool] = None


class TaskOut(TaskBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PartnerActiveStatusOut(BaseModel):
    in_couple: bool
    partner: Optional["UserPartnerSummary"] = None
    is_busy: bool = False
    active_task: Optional[TaskOut] = None

    model_config = ConfigDict(from_attributes=True)


from app.modules.couples.schemas import UserPartnerSummary  # noqa: E402

