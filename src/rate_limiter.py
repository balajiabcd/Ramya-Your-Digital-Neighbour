"""
Redis-based rate limiter for Ramya.
Phase 2: Production Security
"""

import os
import time
import logging
from typing import Optional, Tuple, Dict, Deque
import redis

logger = logging.getLogger(__name__)


class RedisRateLimiter:
    """
    Redis-based sliding window rate limiter.
    """
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self._memory_store: Dict[str, Deque[float]] = {}
        self._lock = None
        self._connect()
    
    def _connect(self):
        """Connect to Redis."""
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        
        try:
            self.redis_client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            self.redis_client.ping()
            logger.info("Redis rate limiter connected successfully")
        except redis.ConnectionError as e:
            logger.warning(f"Redis connection failed, falling back to in-memory: {e}")
            self.redis_client = None
        except Exception as e:
            logger.error(f"Unexpected error connecting to Redis: {e}")
            self.redis_client = None
    
    def is_allowed(self, key: str, limit: int, window: int) -> Tuple[bool, int]:
        """
        Check if request is allowed under rate limit.
        
        Args:
            key: Unique identifier (e.g., IP address or user ID)
            limit: Maximum number of requests allowed
            window: Time window in seconds
            
        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        if self.redis_client is None:
            return self._in_memory_fallback(key, limit, window)
        
        try:
            current_time = time.time()
            window_start = current_time - window
            redis_key = f"ratelimit:{key}"
            
            self.redis_client.zremrangebyscore(redis_key, 0, window_start)
            
            current_count = self.redis_client.zcard(redis_key)
            
            if current_count < limit:
                self.redis_client.zadd(redis_key, {str(current_time): current_time})
                self.redis_client.expire(redis_key, window)
                
                return True, limit - current_count - 1
            else:
                return False, 0
                
        except redis.RedisError as e:
            logger.error(f"Redis error in rate limiter: {e}")
            return self._in_memory_fallback(key, limit, window)
    
    def _in_memory_fallback(self, key: str, limit: int, window: int) -> Tuple[bool, int]:
        """
        Fallback to in-memory rate limiting when Redis is unavailable.
        """
        from collections import deque
        import threading
        
        if self._lock is None:
            self._lock = threading.Lock()
        
        with self._lock:
            current_time = time.time()
            window_start = current_time - window
            
            if key not in self._memory_store:
                self._memory_store[key] = deque()
            
            while self._memory_store[key] and self._memory_store[key][0] < window_start:
                self._memory_store[key].popleft()
            
            current_count = len(self._memory_store[key])
            
            if current_count < limit:
                self._memory_store[key].append(current_time)
                return True, limit - current_count - 1
            else:
                return False, 0
    
    def get_remaining(self, key: str, limit: int, window: int) -> int:
        """Get remaining requests for a key."""
        if self.redis_client is None:
            return limit
        
        try:
            current_time = time.time()
            window_start = current_time - window
            redis_key = f"ratelimit:{key}"
            
            self.redis_client.zremrangebyscore(redis_key, 0, window_start)
            current_count = self.redis_client.zcard(redis_key)
            
            return max(0, limit - current_count)
        except:
            return limit


_rate_limiter: Optional[RedisRateLimiter] = None


def get_rate_limiter() -> RedisRateLimiter:
    """Get or create the rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RedisRateLimiter()
    return _rate_limiter


def check_rate_limit(limit_type: str, identifier: str) -> Tuple[bool, int]:
    """
    Check rate limit for a given type and identifier.
    """
    from src.security_config import get_rate_limit_config
    
    config = get_rate_limit_config()
    rate_config = config.get(limit_type, {'limit': 5, 'window': 60})
    
    limiter = get_rate_limiter()
    return limiter.is_allowed(
        f"{limit_type}:{identifier}",
        rate_config['limit'],
        rate_config['window']
    )
