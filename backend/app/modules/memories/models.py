import uuid
from datetime import date, datetime
from typing import List
from sqlalchemy import String, Text, Date, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Memory(Base):
    __tablename__ = "memories"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    category: Mapped[str] = mapped_column(String(50), default="memory")

    display_type: Mapped[str] = mapped_column(String(50), default="RANDOM")  # 'DATE' or 'RANDOM'
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_shared: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="memories")
    images: Mapped[List["MemoryImage"]] = relationship(
        "MemoryImage",
        back_populates="memory",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="MemoryImage.created_at",
    )


class MemoryImage(Base):
    __tablename__ = "memory_images"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    memory_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("memories.id", ondelete="CASCADE"), nullable=False, index=True)

    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    memory = relationship("Memory", back_populates="images")
