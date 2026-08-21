from typing import Optional
from pydantic import BaseModel


class FrameMeta(BaseModel):
    device_id: str
    timestamp: float
    width: int = 320
    height: int = 240


class BoundingBox(BaseModel):
    label: str
    confidence: float
    x: float
    y: float
    width: float
    height: float


class VisionDetectionResult(BaseModel):
    frame_id: str
    boxes: list[BoundingBox] = []
