from types import SimpleNamespace
from sqlalchemy import delete
from uuid import UUID
import cv2

from app.models.photo import Photo
from app.core.database_sync import SessionLocal
from app.models.face_embedding import FaceEmbedding
from app.services.google_drive import google_drive_service
from app.services.face_recognition import FaceRecognitionService
from app.services.image_decoder import decode_image


face_recognition = FaceRecognitionService()


def process_single_photo(photo_id: str):
    photo_uuid = UUID(photo_id)

    # Phase 1: Retrieve the required data
    with SessionLocal() as db:
        photo = db.get(Photo, photo_uuid)

        if photo is None:
            print(f"Photo not found: {photo_id}")
            return

        if photo.processing_status != "PROCESSING":
            print(f"Skipping photo: {photo_id}")
            return

        user = photo.event.owner

        if not user.refresh_token:
            raise ValueError(
                f"Google refresh token missing for user {user.id}"
            )

        # Copy the required values before closing the session.
        drive_user = SimpleNamespace(
            access_token=user.access_token,
            refresh_token=user.refresh_token,
        )

        drive_file_id = photo.drive_file_id
        filename = photo.filename

    # Phase 2: Download and process outside the DB session
    image_bytes = google_drive_service.download_photo(
        user=drive_user,
        drive_file_id=drive_file_id,
    )

    if not image_bytes:
        raise ValueError("Downloaded image is empty")

    image = decode_image(image_bytes)

    if image is None:
        raise ValueError(f"Could not decode image: {filename}")

    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    embeddings = face_recognition.extract_embeddings(image)

    print(f"Detected {len(embeddings)} faces in {filename}")

    # Phase 3: Persist embeddings and update status atomically
    with SessionLocal() as db:
        photo = db.get(Photo, photo_uuid)

        if photo is None:
            print(f"Photo was deleted during processing: {photo_id}")
            return

        if photo.processing_status != "PROCESSING":
            print(f"Photo is no longer being processed: {photo_id}")
            return

        # Replace any previous embeddings for this photo.
        db.execute(
            delete(FaceEmbedding).where(
                FaceEmbedding.photo_id == photo_uuid
            )
        )

        db.add_all([
            FaceEmbedding(
                photo_id=photo_uuid,
                embedding=embedding,
            )
            for embedding in embeddings
        ])

        photo.processing_status = "COMPLETED"

        db.commit()


def mark_photo_failed(photo_id: UUID):
    with SessionLocal() as db:
        photo = db.get(Photo, photo_id)

        if photo:
            photo.processing_status = 'FAILED'

            db.commit()
