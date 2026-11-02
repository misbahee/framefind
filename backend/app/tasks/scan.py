from sqlalchemy import text

from app.celery_app import celery_app
from app.core.database_sync import SessionLocal


@celery_app.task
def scan_event(a: int, b: int) -> int:
    with SessionLocal() as db:
        value = db.execute(text("SELECT 1")).scalar_one()
        print(f"Database returned: {value}")

    return a + b