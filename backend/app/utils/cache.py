import redis
import json
from typing import Any, Optional
from app.config import settings
import structlog

logger = structlog.get_logger()


class CacheService:
    """Redis-based caching service."""
    
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
        self.default_ttl = settings.CACHE_TTL
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning("Cache get failed", key=key, error=str(e))
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        try:
            ttl = ttl or self.default_ttl
            self.redis.setex(key, ttl, json.dumps(value))
            return True
        except Exception as e:
            logger.warning("Cache set failed", key=key, error=str(e))
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            self.redis.delete(key)
            return True
        except Exception as e:
            logger.warning("Cache delete failed", key=key, error=str(e))
            return False
    
    def get_or_set(self, key: str, func, ttl: Optional[int] = None) -> Any:
        """Get from cache or compute and cache."""
        value = self.get(key)
        if value is not None:
            return value
        
        value = func()
        self.set(key, value, ttl)
        return value
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        try:
            keys = self.redis.keys(pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.warning("Cache clear failed", pattern=pattern, error=str(e))
            return 0


# Singleton instance
cache = CacheService()
