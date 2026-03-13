"""
Tests for src/rate_limiter.py
"""

import pytest
from unittest.mock import patch, MagicMock


class TestRedisRateLimiter:
    """Test Redis-based rate limiter."""
    
    def test_rate_limiter_fallback_to_memory(self):
        """Test rate limiter falls back to in-memory when Redis unavailable."""
        from src.rate_limiter import RedisRateLimiter
        
        with patch.dict('os.environ', {'REDIS_URL': 'redis://localhost:6379/0'}):
            with patch('src.rate_limiter.redis.from_url') as mock_redis:
                # Simulate Redis connection failure
                mock_redis.side_effect = Exception("Connection refused")
                
                limiter = RedisRateLimiter()
                assert limiter.redis_client is None
    
    def test_rate_limiter_creation(self):
        """Test rate limiter can be created."""
        from src.rate_limiter import RedisRateLimiter
        limiter = RedisRateLimiter()
        assert limiter is not None
    
    def test_check_rate_limit_function(self):
        """Test check_rate_limit function."""
        from src.rate_limiter import check_rate_limit
        is_allowed, remaining = check_rate_limit('chat', '127.0.0.1')
        assert isinstance(is_allowed, bool)
        assert isinstance(remaining, int)
    
    def test_rate_limiter_in_memory_fallback(self):
        """Test in-memory fallback works correctly."""
        from src.rate_limiter import RedisRateLimiter
        
        # Create limiter with no Redis
        limiter = RedisRateLimiter()
        limiter.redis_client = None
        
        # Test in-memory fallback
        is_allowed, remaining = limiter._in_memory_fallback('test_key', 5, 60)
        assert is_allowed is True
        assert remaining == 4
