import uuid
from datetime import date, datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, ConfigDict


class MoodBase(BaseModel):
    mood_score: int = Field(..., ge=1, le=10, description="Mood score from 1 (terrible) to 10 (awesome)")
    mood_tag: str = Field(..., min_length=1, max_length=50, description="Mood tag (e.g., happy, calm, tired, anxious)")
    note: Optional[str] = Field(None, max_length=2000, description="Optional journal note or reflection")
    activities: Optional[str] = Field(None, max_length=255, description="Comma-separated activities or tags")
    is_shared: bool = Field(True, description="Whether to share this mood with your partner")


class MoodCreate(MoodBase):
    entry_date: Optional[date] = Field(None, description="Entry date (defaults to today in specified timezone)")
    timezone: Optional[str] = Field("Asia/Ho_Chi_Minh", description="User IANA timezone identifier")


class MoodUpdate(BaseModel):
    mood_score: Optional[int] = Field(None, ge=1, le=10)
    mood_tag: Optional[str] = Field(None, min_length=1, max_length=50)
    note: Optional[str] = Field(None, max_length=2000)
    activities: Optional[str] = Field(None, max_length=255)
    is_shared: Optional[bool] = None
    timezone: Optional[str] = Field("Asia/Ho_Chi_Minh", description="User IANA timezone identifier")


class MoodOut(MoodBase):
    id: uuid.UUID
    user_id: uuid.UUID
    entry_date: date
    is_locked: bool = Field(False, description="True if entry date is strictly before today in user's timezone")
    created_at: datetime
    updated_at: datetime

    user_full_name: Optional[str] = None
    user_avatar_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TodayMoodResponse(BaseModel):
    my_mood: Optional[MoodOut] = None
    partner_mood: Optional[MoodOut] = None


class HeatmapDayItem(BaseModel):
    date: date
    mood_id: Optional[uuid.UUID] = None
    score: Optional[int] = None  # 1 to 10, None if unlogged
    tag: Optional[str] = None
    note: Optional[str] = None
    is_locked: bool = False
    is_today: bool = False

    partner_mood_id: Optional[uuid.UUID] = None
    partner_score: Optional[int] = None
    partner_tag: Optional[str] = None
    partner_note: Optional[str] = None


class HeatmapResponse(BaseModel):
    year: int
    total_logged_days: int
    current_streak: int
    longest_streak: int
    average_score: float
    days: List[HeatmapDayItem]


class MoodStatsResponse(BaseModel):
    total_entries: int
    average_score: float
    mood_counts: Dict[str, int]
    score_distribution: Dict[int, int]
