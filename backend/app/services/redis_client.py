"""
Redis client for caching, rate limiting, and queues
"""

import redis
from typing import Optional
from app.core.config import get_settings

settings = get_settings()

# Redis connections for different purposes
_redis_cache: Optional[redis.Redis] = None
_redis_queue: Optional[redis.Redis] = None
_redis_rate_limit: Optional[redis.Redis] = None


def get_redis_cache() -> redis.Redis:
    """Get Redis connection for caching"""
    global _redis_cache
    if _redis_cache is None:
        _redis_cache = redis.from_url(
            settings.REDIS_URL,
            db=settings.REDIS_CACHE_DB,
            decode_responses=True,
            socket_connect_timeout=5,
        )
    return _redis_cache


def get_redis_queue() -> redis.Redis:
    """Get Redis connection for queues"""
    global _redis_queue
    if _redis_queue is None:
        _redis_queue = redis.from_url(
            settings.REDIS_URL,
            db=settings.REDIS_QUEUE_DB,
            decode_responses=True,
            socket_connect_timeout=5,
        )
    return _redis_queue


def get_redis_rate_limit() -> redis.Redis:
    """Get Redis connection for rate limiting"""
    global _redis_rate_limit
    if _redis_rate_limit is None:
        _redis_rate_limit = redis.from_url(
            settings.REDIS_URL,
            db=settings.REDIS_RATE_LIMIT_DB,
            decode_responses=True,
            socket_connect_timeout=5,
        )
    return _redis_rate_limit


def check_redis_connection() -> bool:
    """Check if Redis is available"""
    try:
        cache = get_redis_cache()
        cache.ping()
        return True
    except Exception:
        return False

