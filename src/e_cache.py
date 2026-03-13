import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

_redis_client = None
_cache_manager = None


def get_redis_client():
    """Get Redis client singleton."""
    global _redis_client
    if _redis_client is None:
        try:
            import redis
            _redis_client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                db=0,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            _redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Using in-memory fallback.")
            _redis_client = None
    return _redis_client


class CacheManager:
    """Redis-based cache manager with in-memory fallback."""
    
    def __init__(self, redis_client=None):
        self.redis = redis_client or get_redis_client()
        self._memory_cache = {}  # Fallback
    
    def get(self, key: str) -> Optional[str]:
        if self.redis:
            try:
                return self.redis.get(key)
            except Exception as e:
                logger.warning(f"Redis get failed: {e}")
        return self._memory_cache.get(key)
    
    def set(self, key: str, value: str, expiry: int = 300) -> bool:
        if self.redis:
            try:
                self.redis.setex(key, expiry, value)
                return True
            except Exception as e:
                logger.warning(f"Redis set failed: {e}")
        self._memory_cache[key] = value
        return True
    
    def delete(self, key: str) -> bool:
        if self.redis:
            try:
                self.redis.delete(key)
                return True
            except Exception as e:
                logger.warning(f"Redis delete failed: {e}")
        self._memory_cache.pop(key, None)
        return True
    
    def increment(self, key: str, expiry: int = 60) -> int:
        if self.redis:
            try:
                pipe = self.redis.pipeline()
                pipe.incr(key)
                pipe.expire(key, expiry)
                result = pipe.execute()
                return result[0]
            except Exception as e:
                logger.warning(f"Redis increment failed: {e}")
        
        # Fallback to in-memory
        current = self._memory_cache.get(key, 0)
        new_value = current + 1
        self._memory_cache[key] = new_value
        return new_value
    
    def get_all_keys(self, pattern: str = "*") -> list:
        if self.redis:
            try:
                return self.redis.keys(pattern)
            except Exception as e:
                logger.warning(f"Redis keys failed: {e}")
        return list(self._memory_cache.keys())


def get_cache() -> CacheManager:
    """Get cache manager singleton."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager
