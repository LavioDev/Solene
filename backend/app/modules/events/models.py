import uuid
from datetime import date, datetime
from sqlalchemy import String, Integer, Date, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class SpecialEvent(Base):
    __tablename__ = "special_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    anchor_date: Mapped[date] = mapped_column(Date, nullable=False)
    recurrence_type: Mapped[str] = mapped_column(String(50), nullable=False, default="EVERY_N_DAYS") # 'EVERY_N_DAYS', 'YEARLY', 'SINGLE'
    interval_value: Mapped[int] = mapped_column(Integer, default=100)
    category: Mapped[str] = mapped_column(String(50), default="love")
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_shared: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="special_events")
