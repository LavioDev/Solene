import uuid
from datetime import datetime, timezone
from typing import Any, Optional
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    device_code: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    mac_address: Mapped[Optional[str]] = mapped_column(
        String(32),
        unique=True,
        index=True,
        nullable=True,
    )
    chip_type: Mapped[str] = mapped_column(
        String(64),
        default="ESP32-S3",
        nullable=False,
    )
    hardware_capabilities: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        default=lambda: {"camera": True, "audio": True, "display": True},
        nullable=False,
    )
    current_config: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        default=lambda: {"fps": 15, "mic_gain": 1.0, "screen_brightness": 100},
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="offline",
        nullable=False,
    )
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    telemetry_logs: Mapped[list["TelemetryLog"]] = relationship(
        "TelemetryLog",
        back_populates="device",
        cascade="all, delete-orphan",
    )


class TelemetryLog(Base):
    __tablename__ = "telemetry_logs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    cpu_temperature: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    free_heap: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    wifi_rssi: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    battery_voltage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    custom_metrics: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
    )

    device: Mapped["Device"] = relationship("Device", back_populates="telemetry_logs")
