"""Celery application instance configuration."""
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "musegen",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.parse_story",
        "app.tasks.generate_assets",
        "app.tasks.generate_keyframes",
        "app.tasks.generate_animation",
        "app.tasks.generate_audio",
        "app.tasks.compose_video",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_soft_time_limit=900,   # 15 minutes soft limit
    task_time_limit=1200,       # 20 minutes hard limit
    result_expires=86400,       # 24h result expiry
)
