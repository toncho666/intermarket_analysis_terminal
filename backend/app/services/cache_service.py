"""
Redis cache service
- Cache calculation results with TTL
- Cache price data
- Session management
"""
import json
import redis
from typing import Optional, Any
from datetime import timedelta
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Redis cache service"""
    
    def __init__(self):
        self.redis_client = None
        self._connect()
    
    def _connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
                socket_timeout=5,
            )
            self.redis_client.ping()
            logger.info("Redis connected")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            self.redis_client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get failed for {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL"""
        if not self.redis_client:
            return False
        
        try:
            serialized = json.dumps(value)
            self.redis_client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Cache set failed for {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.redis_client:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete failed for {key}: {e}")
            return False
    
    def get_prices(self, asset_id: str, frequency: str = "1d") -> Optional[list]:
        """Get cached price data"""
        key = f"prices:{asset_id}:{frequency}"
        return self.get(key)
    
    def set_prices(self, asset_id: str, prices: list, frequency: str = "1d") -> bool:
        """Cache price data"""
        key = f"prices:{asset_id}:{frequency}"
        return self.set(key, prices, ttl=settings.CACHE_TTL_PRICES)
    
    def get_correlation_matrix(self, window: int) -> Optional[dict]:
        """Get cached correlation matrix"""
        key = f"corr_matrix:{window}"
        return self.get(key)
    
    def set_correlation_matrix(self, window: int, matrix: dict) -> bool:
        """Cache correlation matrix"""
        key = f"corr_matrix:{window}"
        return self.set(key, matrix, ttl=settings.CACHE_TTL_CORRELATIONS)
    
    def get_regime(self) -> Optional[dict]:
        """Get cached regime data"""
        key = "regime:current"
        return self.get(key)
    
    def set_regime(self, regime: dict) -> bool:
        """Cache regime data"""
        key = "regime:current"
        return self.set(key, regime, ttl=settings.CACHE_TTL_REGIME)
    
    def invalidate_prices(self, asset_id: Optional[str] = None):
        """Invalidate price cache"""
        if not self.redis_client:
            return
        
        try:
            if asset_id:
                pattern = f"prices:{asset_id}:*"
            else:
                pattern = "prices:*"
            
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"Invalidated {len(keys)} price cache keys")
        except Exception as e:
            logger.error(f"Cache invalidation failed: {e}")
    
    def invalidate_correlations(self):
        """Invalidate correlation cache"""
        if not self.redis_client:
            return
        
        try:
            keys = self.redis_client.keys("corr_matrix:*")
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"Invalidated {len(keys)} correlation cache keys")
        except Exception as e:
            logger.error(f"Correlation cache invalidation failed: {e}")
    
    def health_check(self) -> bool:
        """Check Redis health"""
        if not self.redis_client:
            return False
        
        try:
            return self.redis_client.ping()
        except Exception:
            return False


# Singleton instance
cache_service = CacheService()
