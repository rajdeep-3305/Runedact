import secrets
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Deque, Dict

from fastapi import Header, HTTPException, Request

from app.core.config import settings



def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    if not settings.API_AUTH_ENABLED:
        return
    if not settings.API_KEY:
        raise HTTPException(status_code=503, detail="API auth enabled but API_KEY is not configured")
    if not x_api_key or not secrets.compare_digest(x_api_key, settings.API_KEY):
        raise HTTPException(status_code=401, detail="invalid API key")


@dataclass
class _Bucket:
    timestamps: Deque[float]


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._buckets: Dict[str, _Bucket] = defaultdict(lambda: _Bucket(deque()))

    def _client_key(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        ip = forwarded or (request.client.host if request.client else "unknown")
        return f"{ip}:{request.url.path}"

    def check(self, request: Request) -> None:
        limit = settings.RATE_LIMIT_PER_MINUTE
        if limit <= 0:
            return

        key = self._client_key(request)
        now = time.time()
        window_start = now - 60
        bucket = self._buckets[key].timestamps

        while bucket and bucket[0] < window_start:
            bucket.popleft()

        if len(bucket) >= limit:
            raise HTTPException(status_code=429, detail="rate limit exceeded")

        bucket.append(now)


rate_limiter = InMemoryRateLimiter()
