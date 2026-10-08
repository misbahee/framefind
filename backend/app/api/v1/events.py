from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from uuid import UUID

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.user import User
from app.schemas.event import EventCreate, EventResponse
from app.services.event import event_service
from app.services.google_drive import google_drive_service
from app.schemas.event_membership import EventJoinRequest
from app.schemas.photo import PhotoResponse
from app.services.photo import photo_service


router = APIRouter(
    prefix="/events",
    tags=["Events"],
)


@router.post(
    "",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_event(
    event_data: EventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    event_folder = google_drive_service.create_event_folder(
        user=current_user,
        event_name=event_data.name,
    )

    event = event_service.create_event(
        db=db,
        owner_id=current_user.id,
        name=event_data.name,
        date=event_data.date,
        location=event_data.location,
        description=event_data.description,
        drive_folder_id=event_folder["id"],
    )

    return event


@router.get("", response_model=list[EventResponse])
def list_event(current_user: User = Depends(get_current_user),
               db: Session = Depends(get_db)):
    return event_service.get_user_events(
        db = db,
        user_id= current_user.id,
    )


@router.get(
    "/{event_id}",
    response_model=EventResponse,
)
def get_event(
    event_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    event = event_service.get_user_event(
        db=db,
        event_id=event_id,
        user_id=current_user.id,
    )

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found",
        )

    return event


@router.post(
    "/{event_id}/join",
)
def join_event(
    event_id: UUID,
    join_data: EventJoinRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    event, result = event_service.join_event(
        db=db,
        event_id=event_id,
        user_id=current_user.id,
        invitation_token=join_data.invitation_token,
    )

    if result == "event_not_found":
        raise HTTPException(
            status_code=404,
            detail="Event not found",
        )

    if result == "invalid_invitation":
        raise HTTPException(
            status_code=403,
            detail="Invalid invitation",
        )

    if result == "already_joined":
        return {
            "message": "Already joined",
            "event_id": event.id,
        }

    return {
        "message": "Successfully joined event",
        "event_id": event.id,
    }


@router.post(
    "/{event_id}/photos",
    response_model=PhotoResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_photo(
    event_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    event = event_service.get_user_event(
        db=db,
        event_id=event_id,
        user_id=current_user.id,
    )

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found",
        )

    if event.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only the event owner can upload photos",
        )

    drive_file = google_drive_service.upload_photo(
        user=current_user,
        file=file,
        parent_folder_id=event.drive_folder_id,
    )

    photo = photo_service.create_photo(
        db=db,
        event_id=event.id,
        drive_file_id=drive_file["id"],
        filename=drive_file["name"],
        mime_type=drive_file["mimeType"],
    )

    return photo


@router.get(
    "/{event_id}/photos",
    response_model=list[PhotoResponse],
)
def get_event_photos(
    event_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    photos = photo_service.get_event_photos(
        db=db,
        event_id=event_id,
        user_id=current_user.id,
    )

    if photos is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found",
        )

    return photos

@router.delete("/{event_id}",)
def delete_event():
    pass
