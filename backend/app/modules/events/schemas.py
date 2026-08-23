from uuid import UUID
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SpecialEventCreate(BaseModel):
    title: str
    anchor_date: date
    recurrence_type: str = "EVERY_N_DAYS"  # 'EVERY_N_DAYS', 'MONTHLY', 'YEARLY'
    interval_value: int = 100
    category: str = "love"
    description: Optional[str] = None
    is_shared: bool = True


class SpecialEventUpdate(BaseModel):
    title: Optional[str] = None
    anchor_date: Optional[date] = None
    recurrence_type: Optional[str] = None
    interval_value: Optional[int] = None
    category: Optional[str] = None
    description: Optional[str] = None
    is_shared: Optional[bool] = None


class SpecialEventOut(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    anchor_date: date
    recurrence_type: str
    interval_value: int
    category: str
    description: Optional[str] = None
    is_shared: bool = True
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EventOccurrenceOut(BaseModel):
    event_id: UUID
    title: str
    date: date
    category: str
    milestone_info: Optional[str] = None
    image_url: Optional[str] = None
    is_shared: bool = True
