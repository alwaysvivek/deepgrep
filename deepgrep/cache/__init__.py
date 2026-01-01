"""Redis caching layer for DeepGrep."""

import json
import os
from typing import Any, Optional
from functools import wraps
import hashlib


class CacheManager:
    """Redis cache manager."""

    def __init__(self, redis_url: str = None):
        """
        Initialize Redis connection.

        Args:
            redis_url: Redis connection string (e.g., redis://localhost:6379/0)
        """
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis_client = None
        self._connect()

    def _connect(self):
        """Connect to Redis."""
        try:
            import redis
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            self.redis_client.ping()
        except ImportError:
            print("Warning: redis package not installed. Caching disabled.")
            self.redis_client = None
        except Exception as e:
            print(f"Warning: Could not connect to Redis: {e}. Caching disabled.")
            self.redis_client = None

    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a cache key from arguments."""
        key_parts = [prefix] + [str(arg) for arg in args]
        if kwargs:
            key_parts.append(json.dumps(kwargs, sort_keys=True))
        key_string = ":".join(key_parts)
        return f"deepgrep:{hashlib.md5(key_string.encode()).hexdigest()}"

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.redis_client:
            return None

        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            print(f"Cache get error: {e}")
        return None

    def set(self, key: str, value: Any, ttl: int = 3600):
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: 1 hour)
        """
        if not self.redis_client:
            return

        try:
            self.redis_client.setex(key, ttl, json.dumps(value))
        except Exception as e:
            print(f"Cache set error: {e}")

    def delete(self, key: str):
        """Delete key from cache."""
        if not self.redis_client:
            return

        try:
            self.redis_client.delete(key)
        except Exception as e:
            print(f"Cache delete error: {e}")

    def clear(self, pattern: str = "deepgrep:*"):
        """Clear cache keys matching pattern."""
        if not self.redis_client:
            return

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
        except Exception as e:
            print(f"Cache clear error: {e}")


def cached(prefix: str, ttl: int = 3600):
    """
    Decorator to cache function results.

    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds

    Usage:
        @cached("search", ttl=300)
        def search_function(query):
            return expensive_operation(query)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = CacheManager()
            cache_key = cache._generate_key(prefix, *args, **kwargs)

            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Compute and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result

        return wrapper
    return decorator
