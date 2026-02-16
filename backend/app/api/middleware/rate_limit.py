"""
Rate limiting middleware using Redis (with in-memory fallback)
"""

import time
import threading
from collections import defaultdict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.config import get_settings
from app.services.redis_client import get_redis_rate_limit

import logging
logger = logging.getLogger(__name__)

settings = get_settings()

# In-memory fallback rate limiter
_memory_store: dict[str, list[float]] = defaultdict(list)
_memory_lock = threading.Lock()

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""

    async def dispatch(self, request: Request, call_next):
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)

        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/"]:
            return await call_next(request)

        # Get client identifier
        client_id = self._get_client_id(request)

        # Check rate limits
        if not self._check_rate_limit(client_id, request.url.path):
            return Response(
                content='{"detail": "Rate limit exceeded"}',
                status_code=429,
                media_type="application/json",
                headers={
                    "X-RateLimit-Limit": str(settings.RATE_LIMIT_PER_MINUTE),
                    "X-RateLimit-Retry-After": "60",
                },
            )

        # Add rate limit headers
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_PER_MINUTE)
        response.headers["X-RateLimit-Remaining"] = str(
            self._get_remaining_requests(client_id)
        )

        return response

    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting"""
        # Try API key first
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api_key:{api_key[:8]}"

        # Fall back to IP address
        client_host = request.client.host if request.client else "unknown"
        return f"ip:{client_host}"

    def _check_rate_limit(self, client_id: str, path: str) -> bool:
        """Check if request is within rate limit"""
        try:
            redis_client = get_redis_rate_limit()

            # Per-minute limit
            minute_key = f"rate_limit:minute:{client_id}:{path}"
            minute_count = redis_client.incr(minute_key)
            if minute_count == 1:
                redis_client.expire(minute_key, 60)
            if minute_count > settings.RATE_LIMIT_PER_MINUTE:
                return False

            # Per-hour limit
            hour_key = f"rate_limit:hour:{client_id}:{path}"
            hour_count = redis_client.incr(hour_key)
            if hour_count == 1:
                redis_client.expire(hour_key, 3600)
            if hour_count > settings.RATE_LIMIT_PER_HOUR:
                return False

            return True
        except Exception:
            # Redis unavailable — use in-memory fallback
            return self._check_rate_limit_memory(client_id, path)

    def _get_remaining_requests(self, client_id: str) -> int:
        """Get remaining requests for client"""
        try:
            redis_client = get_redis_rate_limit()
            minute_key = f"rate_limit:minute:{client_id}:*"
            return max(0, settings.RATE_LIMIT_PER_MINUTE - 1)
        except Exception:
            return settings.RATE_LIMIT_PER_MINUTE

    def _check_rate_limit_memory(self, client_id: str, path: str) -> bool:
        """In-memory fallback when Redis is unavailable"""
        now = time.time()
        key = f"{client_id}:{path}"
        with _memory_lock:
            # Clean old entries (older than 60s)
            _memory_store[key] = [t for t in _memory_store[key] if now - t < 60]
            if len(_memory_store[key]) >= settings.RATE_LIMIT_PER_MINUTE:
                return False
            _memory_store[key].append(now)
            return True

