from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.photo import Photo
from app.models.event import Event
from app.models.event_membership import EventMembership


class PhotoService:

    async def create_photo(
        self,
        db: AsyncSession,
        event_id: UUID,
        drive_file_id: str,
        filename: str,
        mime_type: str,
    ):
        """Create a photo record after the file is uploaded to Google Drive."""
        photo = Photo(
            event_id=event_id,
            drive_file_id=drive_file_id,
            filename=filename,
            mime_type=mime_type,
            processing_status="PENDING",
        )

        db.add(photo)
        await db.commit()
        await db.refresh(photo)

        return photo


    async def get_event_photos(
        self,
        db: AsyncSession,
        event_id: UUID,
        user_id: UUID,
    ):
        """Return photos from an event if the user has access to it."""

        access_statement = (
            select(Event.id)
            .outerjoin(
                EventMembership,
                (EventMembership.event_id == Event.id)
                & (EventMembership.user_id == user_id),
            )
            .where(
                Event.id == event_id,
                (
                    (Event.owner_id == user_id)
                    | (EventMembership.user_id == user_id)
                ),
            )
        )

        event = await db.scalar(access_statement)

        if event is None:
            return None

        statement = (
            select(Photo)
            .where(Photo.event_id == event_id)
            .order_by(Photo.created_at.desc())
        )

        result = await db.scalars(statement)
        return result.all()


    async def claim_pending_photos(
        self,
        db: AsyncSession,
        event_id: UUID,
        batch_size: int = 100,
    ):
        """Finds photos with the \'PENDING\' status and returns it also locks that rows."""
        
        stmt = (
            select(Photo)
            .where(
                Photo.event_id == event_id,
                Photo.processing_status == "PENDING",
            )
            .limit(batch_size)
            .with_for_update(skip_locked=True)
        )

        result = await db.execute(stmt)

        return result.scalars().all()


photo_service = PhotoService()
