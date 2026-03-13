"""
Tests for src/security_config.py
"""

import os
import pytest
from unittest.mock import patch


class TestSecurityConfig:
    """Test security configuration."""
    
    def test_get_security_headers_development(self):
        """Test security headers in development."""
        with patch.dict(os.environ, {'APP_ENV': 'Development'}):
            from src.security_config import get_security_headers
            headers = get_security_headers()
            assert headers['force_https'] is False
    
    def test_get_security_headers_production(self):
        """Test security headers in production."""
        with patch.dict(os.environ, {'APP_ENV': 'Production'}):
            from src.security_config import get_security_headers
            headers = get_security_headers()
            assert headers['force_https'] is True
            assert 'max-age=31536000' in headers['strict_transport_security']
    
    def test_get_cors_config_default(self):
        """Test default CORS config."""
        with patch.dict(os.environ, {'CORS_ALLOWED_ORIGINS': ''}):
            from src.security_config import get_cors_config
            config = get_cors_config()
            assert 'http://localhost:8080' in config['origins']
    
    def test_get_cors_config_custom(self):
        """Test custom CORS config."""
        with patch.dict(os.environ, {'CORS_ALLOWED_ORIGINS': 'https://example.com'}):
            from src.security_config import get_cors_config
            config = get_cors_config()
            assert 'https://example.com' in config['origins']
    
    def test_get_rate_limit_config(self):
        """Test rate limit config."""
        from src.security_config import get_rate_limit_config
        config = get_rate_limit_config()
        assert 'chat' in config
        assert 'tts' in config
        assert 'stt' in config
        assert config['chat']['limit'] == 5
