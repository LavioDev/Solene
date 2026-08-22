import uuid
from datetime import date
from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Couple(Base):
    __tablename__ = "couples"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user1_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user2_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    nickname: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    cover_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    user1 = relationship("User", foreign_keys=[user1_id], backref="couples_as_user1", lazy="joined")
    user2 = relationship("User", foreign_keys=[user2_id], backref="couples_as_user2", lazy="joined")
