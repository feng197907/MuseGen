"""Celery worker entry point."""
from app.tasks.celery_app import celery_app  # noqa: F401
# Import all tasks to register them with Celery
import app.tasks.parse_story  # noqa: F401
import app.tasks.generate_assets  # noqa: F401
import app.tasks.generate_keyframes  # noqa: F401
import app.tasks.generate_animation  # noqa: F401
import app.tasks.generate_audio  # noqa: F401
import app.tasks.compose_video  # noqa: F401

if __name__ == "__main__":
    celery_app.start()
