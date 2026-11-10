from PIL import UnidentifiedImageError
import cv2
from fastapi import APIRouter, Depends, Request, status, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool
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
from app.tasks.photo_tasks import process_photo
from app.services.image_decoder import decode_image
from app.services.photo_search import search_similar_photos
from app.core.config import settings

router = APIRouter(
    prefix="/events",
    tags=["Events"],
)


@router.post(
    "",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_event(
    event_data: EventCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    event_folder = await run_in_threadpool(
        google_drive_service.create_event_folder,
        user=current_user,
        event_name=event_data.name,
    )

    event = await event_service.create_event(
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
async def list_event(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await event_service.get_user_events(
        db=db,
        user_id=current_user.id,
    )


@router.get(
    "/{event_id}",
    response_model=EventResponse,
)
async def get_event(
    event_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    event = await event_service.get_user_event(
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
async def join_event(
    event_id: UUID,
    join_data: EventJoinRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    event, result = await event_service.join_event(
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
async def upload_photo(
    event_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    event = await event_service.get_user_event(
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

    drive_file = await run_in_threadpool(
        google_drive_service.upload_photo,
        user=current_user,
        file=file,
        parent_folder_id=event.drive_folder_id,
    )

    photo = await photo_service.create_photo(
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
async def get_event_photos(
    event_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    photos = await photo_service.get_event_photos(
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


@router.post("/{event_id}/scan")
async def photo_scan(
    event_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Event admin can schedule face embedding in background. This will pass photo_id to Redis then the celery handles those,
    which haven't processed yet. We use row locks so concurrent scan request wont make duplicate entries.
    """

    event = await event_service.get_user_event(
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
            detail="Only the event owner can scan",
        )
    # End the transaction used for the event lookup.
    await db.rollback()

    # Start a new transaction for photo claiming.
    async with db.begin():
        photos = await photo_service.claim_pending_photos(
            db=db,
            event_id=event_id,
            batch_size=100,
        )

        for photo in photos:
            photo.processing_status = "PROCESSING"

        photo_ids = [photo.id for photo in photos]

    # Transaction has committed here, when it exits this block.
    # Row locks have been released.

    # Celery dispatch will go here next.
    if photo_ids:
        for photo_id in photo_ids:
            await run_in_threadpool(
                process_photo.delay,
                str(photo_id)
                )

    return {
        "event_id": str(event_id),
        "photos_queued": len(photo_ids),
        "photo_ids": [str(pid) for pid in photo_ids],
    }


@router.post("/{event_id}/search")
async def search_event_photos(
    event_id: UUID,
    request: Request,
    selfie: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    get a photo from user, embed it returns the photos where that face has appeared.
    """

    # 1. Verify event access
    event = await event_service.get_user_event(
        db=db,
        event_id=event_id,
        user_id=current_user.id,
    )

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found",
        )
    
    MAX_SELFIE_SIZE = settings.MAX_SELFIE_SIZE
    # 2. Read uploaded selfie
    image_bytes = await selfie.read(MAX_SELFIE_SIZE + 1)

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded image is empty",
        )

    if len(image_bytes) > MAX_SELFIE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Selfie must be smaller than 10 MB",
        )

    # 3. Decode image using existing decoder
    try:
        rgb_image = decode_image(image_bytes)

    except (UnidentifiedImageError, OSError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="Invalid or unsupported image",
        )

    # 4. Convert RGB to BGR for InsightFace
    bgr_image = cv2.cvtColor(
        rgb_image,
        cv2.COLOR_RGB2BGR,
    )

    # 5. Get FaceRecognitionService from FastAPI lifespan
    face_recognition = request.app.state.face_recognition

    # 6. Extract face embeddings
    embeddings = await run_in_threadpool(
        face_recognition.extract_embeddings,
        bgr_image,
    )

    # 7. Validate detected faces
    if len(embeddings) == 0:
        raise HTTPException(
            status_code=400,
            detail="No face detected in the uploaded selfie",
        )

    if len(embeddings) > 1:
        raise HTTPException(
            status_code=400,
            detail="Please upload a selfie containing only one face",
        )

    query_embedding = embeddings[0]

    # 8. Search similar photos in PostgreSQL
    matches = await search_similar_photos(
        db=db,
        event_id=event_id,
        query_embedding=query_embedding,
    )

    # 9. Return results
    return {
        "event_id": str(event_id),
        "total_matches": len(matches),
        "matches": matches,
    }
    

@router.delete("/{event_id}")
async def delete_event():
    pass

