from celery import Celery

from app.core.config import settings


celery_app = Celery(
    "framefind",
    broker=settings.BROKER_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],    
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
)

