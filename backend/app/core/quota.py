"""Simple API quota management middleware."""
import time
from collections import defaultdict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings


class QuotaMiddleware(BaseHTTPMiddleware):
    """In-memory daily rate limiter for API endpoints.

    Tracks image & video generation call counts per day.
    In production, replace with Redis-backed counters.
    """

    def __init__(self, app):
        super().__init__(app)
        self._image_counts: dict[str, int] = defaultdict(int)
        self._video_counts: dict[str, int] = defaultdict(int)
        self._day = time.strftime("%Y-%m-%d")

    async def dispatch(self, request: Request, call_next):
        today = time.strftime("%Y-%m-%d")
        if today != self._day:
            self._image_counts.clear()
            self._video_counts.clear()
            self._day = today

        path = request.url.path

        if "/generate/" in path:
            if "keyframe" in path or "asset" in path:
                key = request.client.host if request.client else "unknown"
                self._image_counts[key] += 1
                if self._image_counts[key] > settings.MAX_DAILY_IMAGE_CALLS:
                    raise HTTPException(
                        status_code=429,
                        detail=f"Daily image generation limit ({settings.MAX_DAILY_IMAGE_CALLS}) reached",
                    )
            elif "animation" in path:
                key = request.client.host if request.client else "unknown"
                self._video_counts[key] += 1
                if self._video_counts[key] > settings.MAX_DAILY_VIDEO_CALLS:
                    raise HTTPException(
                        status_code=429,
                        detail=f"Daily video generation limit ({settings.MAX_DAILY_VIDEO_CALLS}) reached",
                    )

        return await call_next(request)
