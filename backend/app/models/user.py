import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Boolean, DateTime, JSON, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    hobbies = mapped_column(JSON, default=list)
    age_range = mapped_column(String(20), nullable=True, default=None)
    life_situations = mapped_column(JSON, default=list)
    city = mapped_column(String(100), nullable=True, default=None)
    province = mapped_column(String(50), nullable=True, default=None)
    radius = mapped_column(Integer, nullable=True, default=None)
    bio = mapped_column(Text, nullable=True, default=None)
    avatar_url = mapped_column(String(500), nullable=True, default=None)
    visibility = mapped_column(JSON, default=dict)

    # Hilos creados por esta usuaria (relación uno-a-muchos con Thread).
    threads = relationship("Thread", back_populates="author")

    # Respuestas escritas por esta usuaria (relación uno-a-muchos con Reply).
    replies = relationship("Reply", back_populates="author")
