from app.celery_app import celery_app
from app.services.photo_processing import process_single_photo, mark_photo_failed

@celery_app.task(
    bind=True,
    max_retries=2,
    name="app.tasks.photo_tasks.process_photo",
)
def process_photo(self, photo_id: str):

    try:
        process_single_photo(photo_id)

    except Exception as exc:

        if self.request.retries < self.max_retries:
            raise self.retry(
                exc=exc,
                countdown=30 if self.request.retries == 0 else 120,
            )

        mark_photo_failed(photo_id)
