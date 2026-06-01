"""Server-Sent Events endpoint for real-time task progress."""
import asyncio
import json
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from app.core.redis_client import get_redis

router = APIRouter()

SSE_CHANNEL_PREFIX = "task:progress:"


@router.get("/tasks/{task_id}")
async def sse_task_progress(task_id: str, request: Request):
    """Stream task progress updates via SSE."""

    async def event_generator():
        redis = get_redis()
        channel = f"{SSE_CHANNEL_PREFIX}{task_id}"
        pubsub = redis.pubsub()
        await pubsub.subscribe(channel)

        try:
            # Send initial connection event
            yield f"data: {json.dumps({'taskId': task_id, 'status': 'running', 'progress': 0, 'currentStep': 'connecting...', 'taskType': '', 'message': 'SSE connected'})}\n\n"

            while True:
                # Check if client disconnected
                if await request.is_disconnected():
                    break

                try:
                    message = await asyncio.wait_for(
                        pubsub.get_message(ignore_subscribe_messages=True),
                        timeout=30,
                    )
                    if message:
                        yield f"data: {message['data']}\n\n"

                        # Check for terminal status
                        try:
                            data = json.loads(message["data"])
                            if data.get("status") in ("done", "failed"):
                                break
                        except json.JSONDecodeError:
                            pass
                except asyncio.TimeoutError:
                    # Send keepalive ping
                    yield ": keepalive\n\n"

        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.aclose()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
