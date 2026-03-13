"""
Tests for src/d_security_utils.py
"""

import pytest
from unittest.mock import patch, MagicMock


class TestSecurityUtils:
    """Test security utilities."""
    
    def test_sanitize_string_basic(self):
        """Test basic string sanitization."""
        from src.d_security_utils import sanitize_string
        result = sanitize_string("Hello World")
        assert result == "Hello World"
    
    def test_sanitize_string_special_chars(self):
        """Test sanitization removes special characters."""
        from src.d_security_utils import sanitize_string
        result = sanitize_string("Hello <script>alert('xss')</script>")
        assert "<script>" not in result
    
    def test_sanitize_string_empty(self):
        """Test sanitization handles empty string."""
        from src.d_security_utils import sanitize_string
        result = sanitize_string("")
        assert result == ""
    
    def test_detect_injection_sql(self):
        """Test SQL injection detection."""
        from src.d_security_utils import detect_injection
        result = detect_injection("SELECT * FROM users")
        assert result is True
    
    def test_detect_injection_normal(self):
        """Test normal text doesn't trigger injection detection."""
        from src.d_security_utils import detect_injection
        result = detect_injection("Hello, how are you?")
        assert result is False
    
    def test_validate_api_key_valid(self):
        """Test valid API key format."""
        from src.d_security_utils import validate_api_key
        # Should not raise exception
        validate_api_key("sk-or-v1-abc12345678901234567890123")
    
    def test_validate_api_key_empty(self):
        """Test empty API key."""
        from src.d_security_utils import validate_api_key
        with pytest.raises(ValueError):
            validate_api_key("")
    
    def test_validate_api_key_none(self):
        """Test None API key."""
        from src.d_security_utils import validate_api_key
        with pytest.raises(ValueError):
            validate_api_key(None)


class TestRateLimiter:
    """Test in-memory rate limiter."""
    
    def test_rate_limiter_allows_within_limit(self):
        """Test rate limiter allows requests within limit."""
        from src.d_security_utils import RateLimiter
        limiter = RateLimiter(limit=5, window=60)
        
        # First 5 requests should be allowed
        for i in range(5):
            assert limiter.is_allowed("test_key") is True
    
    def test_rate_limiter_blocks_over_limit(self):
        """Test rate limiter blocks requests over limit."""
        from src.d_security_utils import RateLimiter
        limiter = RateLimiter(limit=2, window=60)
        
        # First 2 requests allowed
        assert limiter.is_allowed("test_key") is True
        assert limiter.is_allowed("test_key") is True
        # 3rd request should be blocked
        assert limiter.is_allowed("test_key") is False
    
    def test_rate_limiter_different_keys(self):
        """Test rate limiter allows different keys."""
        from src.d_security_utils import RateLimiter
        limiter = RateLimiter(limit=1, window=60)
        
        assert limiter.is_allowed("key1") is True
        assert limiter.is_allowed("key2") is True
        assert limiter.is_allowed("key3") is True
