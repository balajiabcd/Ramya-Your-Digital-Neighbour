"""
Tests for src/config.py
"""

import os
import pytest
from unittest.mock import patch, MagicMock


class TestConfig:
    """Test configuration module."""
    
    def test_config_loads_development(self):
        """Test config loads development environment."""
        with patch.dict(os.environ, {'APP_ENV': 'development'}):
            from src.config import get_config, reset_config
            reset_config()
            config = get_config()
            assert config.env == 'Development'
            assert config.debug is True
    
    def test_config_loads_production(self):
        """Test config loads production environment."""
        with patch.dict(os.environ, {
            'APP_ENV': 'production',
            'SECRET_KEY': 'test-secret-key-min-32-characters-long',
            'OPENROUTER_API_KEY': 'test-key'
        }):
            from src.config import get_config, reset_config
            reset_config()
            config = get_config()
            assert config.env == 'Production'
            assert config.debug is False
    
    def test_config_invalid_env(self):
        """Test config fails with invalid environment."""
        with patch.dict(os.environ, {'APP_ENV': 'invalid'}):
            from src.config import get_config, reset_config, ConfigError
            reset_config()
            with pytest.raises(ConfigError):
                get_config()
    
    def test_config_port(self):
        """Test config port setting."""
        with patch.dict(os.environ, {'PORT': '9000'}):
            from src.config import get_config, reset_config
            reset_config()
            config = get_config()
            assert config.port == 9000
    
    def test_config_cors_origins(self):
        """Test CORS origins configuration."""
        with patch.dict(os.environ, {
            'CORS_ALLOWED_ORIGINS': 'https://example.com,https://app.example.com'
        }):
            from src.config import get_config, reset_config
            reset_config()
            config = get_config()
            assert 'https://example.com' in config.security.cors_allowed_origins
    
    def test_config_rate_limits(self):
        """Test rate limiting configuration."""
        with patch.dict(os.environ, {
            'RATE_LIMIT_CHAT': '10',
            'RATE_LIMIT_TTS': '20'
        }):
            from src.config import get_config, reset_config
            reset_config()
            config = get_config()
            assert config.security.rate_limit_chat == 10
            assert config.security.rate_limit_tts == 20
    
    def test_config_paths(self):
        """Test paths configuration."""
        with patch.dict(os.environ, {
            'CHROMADB_PATH': '/custom/path',
            'LOG_DIR': '/custom/logs'
        }):
            from src.config import get_config, reset_config
            reset_config()
            config = get_config()
            assert config.paths.chromadb_path == '/custom/path'
            assert config.paths.log_dir == '/custom/logs'
    
    def test_config_validation_warnings(self):
        """Test config validation warnings."""
        with patch.dict(os.environ, {'APP_ENV': 'production'}):
            from src.config import get_config, reset_config
            reset_config()
            config = get_config()
            warnings = config.validate()
            assert len(warnings) > 0
    
    def test_session_cookie_secure_production(self):
        """Test session cookie is secure in production."""
        with patch.dict(os.environ, {
            'APP_ENV': 'production',
            'SECRET_KEY': 'test-secret-key-min-32-characters-long'
        }):
            from src.config import get_config, reset_config
            reset_config()
            config = get_config()
            assert config.security.session_cookie_secure is True
    
    def test_session_cookie_insecure_development(self):
        """Test session cookie is not secure in development."""
        with patch.dict(os.environ, {'APP_ENV': 'development'}):
            from src.config import get_config, reset_config
            reset_config()
            config = get_config()
            assert config.security.session_cookie_secure is False
