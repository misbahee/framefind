from app.celery_app import celery_app
from app.services.photo_processing import process_single_photo


@celery_app.task
def process_photos(photo_ids: list[str]):

    print(f"Received {len(photo_ids)} photos for processing")

    for photo_id in photo_ids:
        try:
            process_single_photo(photo_id)

        except Exception as exc:
            print(f"Failed to process photo {photo_id}: {exc}")

    print("Photo batch processing finished")