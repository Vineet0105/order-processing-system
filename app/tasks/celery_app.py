
from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "order_processing",
    broker=settings.redis_url,
    include=["app.tasks.order_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_track_started=True,
    result_expires=3600,
    timezone="UTC",
    enable_utc=True,
)
