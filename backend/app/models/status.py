"""SQLAlchemy ORM model for the StatusUpdate entity."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User

VALID_CATEGORIES = ("done", "in-progress", "blocked", "planning")
_CATEGORY_IN_CLAUSE = ", ".join(f"'{c}'" for c in VALID_CATEGORIES)


class StatusUpdate(Base):
    """A status update posted by a user."""

    __tablename__ = "status_updates"
    __table_args__ = (
        CheckConstraint(
            f"category IN ({_CATEGORY_IN_CLAUSE})",
            name="ck_status_updates_category",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    message: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="status_updates", lazy="raise")

    def __repr__(self) -> str:
        return f"StatusUpdate(id={self.id!r}, user_id={self.user_id!r})"
