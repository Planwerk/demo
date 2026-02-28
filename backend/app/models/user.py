"""SQLAlchemy ORM model for the User entity."""

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.status import StatusUpdate


class User(Base):
    """A registered user who can post status updates."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    display_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    avatar_url: Mapped[str | None] = mapped_column(String(500), default=None)
    xp: Mapped[int] = mapped_column(default=0, server_default="0")
    current_streak: Mapped[int] = mapped_column(default=0, server_default="0")
    longest_streak: Mapped[int] = mapped_column(default=0, server_default="0")
    last_post_date: Mapped[date | None] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    status_updates: Mapped[list["StatusUpdate"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="raise",
    )

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r})"
