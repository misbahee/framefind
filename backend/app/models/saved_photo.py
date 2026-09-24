import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class SavedPhoto(Base):
    __tablename__ = "saved_photos"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "photo_id",
            name="uq_saved_photo",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    photo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("photos.id"),
        nullable=False,
    )

    destination_drive_file_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    event_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default= lambda : datetime.now(timezone.utc),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="saved_photos",
    )

    photo: Mapped["Photo"] = relationship(
        back_populates="saved_photos",
    )