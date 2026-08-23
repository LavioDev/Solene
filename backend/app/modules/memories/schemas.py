from uuid import UUID
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class MemoryImageOut(BaseModel):
    id: UUID
    memory_id: UUID
    file_path: str
    filename: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MemoryCreate(BaseModel):
    title: str
    content: str
    image_url: Optional[str] = None
    image_urls: Optional[List[str]] = None
    category: str = "memory"
    display_type: str = "RANDOM"  # 'DATE' or 'RANDOM'
    target_date: Optional[date] = None
    is_shared: bool = True


class MemoryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None
    image_urls: Optional[List[str]] = None
    category: Optional[str] = None
    display_type: Optional[str] = None
    target_date: Optional[date] = None
    is_shared: Optional[bool] = None


class MemoryOut(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    content: str
    image_url: Optional[str] = None
    images: List[MemoryImageOut] = []
    category: str
    display_type: str
    target_date: Optional[date] = None
    is_shared: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
