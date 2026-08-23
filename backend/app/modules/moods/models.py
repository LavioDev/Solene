import uuid
from datetime import date, datetime, timezone
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class UserMood(Base):
    __tablename__ = "user_moods"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    entry_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    mood_score: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 (Terrible) to 10 (Awesome)
    mood_tag: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., 'happy', 'excited', 'calm', 'tired', 'anxious', 'sad', 'angry'
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    activities: Mapped[str | None] = mapped_column(String(255), nullable=True)  # Comma-separated tags or activities
    is_shared: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user = relationship("User", backref="moods", lazy="selectin")

    __table_args__ = (
        UniqueConstraint("user_id", "entry_date", name="uq_user_mood_entry_date"),
    )
