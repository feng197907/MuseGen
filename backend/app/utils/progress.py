"""Progress publishing utility — sends task updates via Redis Pub/Sub for SSE."""
import json
from app.core.redis_client import get_redis

SSE_CHANNEL_PREFIX = "task:progress:"


def update_progress(
    task_id: str,
    task_type: str,
    status: str,
    progress: float,
    message: str,
):
    """Publish a progress update to the Redis SSE channel.

    Args:
        task_id: The async task ID.
        task_type: Task type label (e.g. 'parse_story').
        status: Task status (running/done/failed).
        progress: Progress percentage (0-100).
        message: Human-readable status message.
    """
    payload = json.dumps({
        "taskId": task_id,
        "taskType": task_type,
        "status": status,
        "progress": progress,
        "currentStep": message,
        "message": message,
    })

    try:
        redis = get_redis()
        import redis.asyncio
        # Use sync publish since Celery tasks are sync
        channel = f"{SSE_CHANNEL_PREFIX}{task_id}"
        # Must use sync Redis connection for Celery tasks
        import redis
        sync_redis = redis.Redis.from_url(
            "redis://localhost:6379/0",
            encoding="utf-8",
            decode_responses=True,
        )
        sync_redis.publish(channel, payload)
        sync_redis.close()
    except Exception:
        pass  # Don't let logging failure crash the task
