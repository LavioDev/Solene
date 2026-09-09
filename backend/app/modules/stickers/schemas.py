from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class PinnedStickerBase(BaseModel):
    sticker_url: str = Field(..., max_length=500, description="Relative or absolute URL to sticker image")
    name: Optional[str] = Field(None, max_length=100)
    x_percent: float = Field(50.0, ge=0.0, le=100.0, description="X position in percentage of canvas width")
    y_percent: float = Field(50.0, ge=0.0, le=100.0, description="Y position in percentage of canvas height")
    scale: float = Field(1.0, ge=0.2, le=3.0, description="Scale factor")
    rotation: float = Field(0.0, ge=-180.0, le=180.0, description="Rotation angle in degrees")
    z_index: int = Field(10, ge=0, le=1000, description="Stacking layer order")
    is_locked: bool = Field(False, description="Whether the sticker is locked/pinned in place")


class PinnedStickerCreate(PinnedStickerBase):
    pass


class PinnedStickerUpdate(BaseModel):
    x_percent: Optional[float] = Field(None, ge=0.0, le=100.0)
    y_percent: Optional[float] = Field(None, ge=0.0, le=100.0)
    scale: Optional[float] = Field(None, ge=0.2, le=3.0)
    rotation: Optional[float] = Field(None, ge=-180.0, le=180.0)
    z_index: Optional[int] = Field(None, ge=0, le=1000)
    is_locked: Optional[bool] = Field(None)


class PinnedStickerBatchItem(BaseModel):
    id: UUID
    x_percent: float = Field(..., ge=0.0, le=100.0)
    y_percent: float = Field(..., ge=0.0, le=100.0)
    scale: float = Field(1.0, ge=0.2, le=3.0)
    rotation: float = Field(0.0, ge=-180.0, le=180.0)
    z_index: int = Field(10, ge=0, le=1000)
    is_locked: Optional[bool] = Field(None)


class PinnedStickerBatchSync(BaseModel):
    stickers: List[PinnedStickerBatchItem]


class PinnedStickerOut(PinnedStickerBase):
    id: UUID
    couple_id: UUID
    user_id: UUID
    user_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
