import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    google_user_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    google_profile_photo: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    access_token: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    refresh_token: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    token_expiry: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    framefind_folder_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda : datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda : datetime.now(timezone.utc),
        onupdate=lambda : datetime.now(timezone.utc),
        nullable=False,
    )

    events: Mapped[list["Event"]] = relationship(
        back_populates="owner",
    )

    memberships: Mapped[list["EventMembership"]] = relationship(
        back_populates="user",
    )

    saved_photos: Mapped[list["SavedPhoto"]] = relationship(
        back_populates="user",
    )