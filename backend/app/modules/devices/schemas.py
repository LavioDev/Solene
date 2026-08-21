import uuid
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict


class DeviceBase(BaseModel):
    device_code: str
    name: str
    mac_address: Optional[str] = None
    chip_type: Optional[str] = "ESP32-S3"
    hardware_capabilities: Optional[dict[str, Any]] = None
    current_config: Optional[dict[str, Any]] = None
    status: Optional[str] = "offline"


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    chip_type: Optional[str] = None
    hardware_capabilities: Optional[dict[str, Any]] = None
    current_config: Optional[dict[str, Any]] = None
    status: Optional[str] = None


class DeviceOut(DeviceBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    last_seen_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class TelemetryIn(BaseModel):
    cpu_temperature: Optional[float] = None
    free_heap: Optional[int] = None
    wifi_rssi: Optional[int] = None
    battery_voltage: Optional[float] = None
    custom_metrics: Optional[dict[str, Any]] = None


class TelemetryOut(TelemetryIn):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: uuid.UUID
    created_at: datetime
