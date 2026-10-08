from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.photo import Photo
from app.models.event import Event
from app.models.event_membership import EventMembership

from app.models.photo import Photo


class PhotoService:

    def create_photo(
        self,
        db: Session,
        event_id,
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
        db.commit()
        db.refresh(photo)

        return photo


    def get_event_photos(
        self,
        db: Session,
        event_id,
        user_id,
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

        event = db.scalar(access_statement)

        if event is None:
            return None

        statement = (
            select(Photo)
            .where(Photo.event_id == event_id)
            .order_by(Photo.created_at.desc())
        )

        return db.scalars(statement).all()



photo_service = PhotoService()
