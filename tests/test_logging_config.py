"""
Tests for src/logging_config.py
"""

import os
import pytest
import logging
from unittest.mock import patch, MagicMock


class TestLoggingConfig:
    """Test logging configuration."""
    
    def test_setup_logging_development(self, temp_dir):
        """Test logging setup in development."""
        logger = logging.getLogger()
        logger.handlers.clear()
        
        from src.logging_config import setup_logging
        result = setup_logging('Development', str(temp_dir))
        
        assert result is not None
        assert len(logger.handlers) > 0
    
    def test_setup_logging_production(self, temp_dir):
        """Test logging setup in production."""
        logger = logging.getLogger()
        logger.handlers.clear()
        
        from src.logging_config import setup_logging
        result = setup_logging('Production', str(temp_dir))
        
        assert result is not None
    
    def test_get_logger(self):
        """Test get_logger function."""
        from src.logging_config import get_logger
        logger = get_logger('test')
        assert logger.name == 'test'
    
    def test_json_formatter(self):
        """Test JSON formatter."""
        from src.logging_config import JSONFormatter
        formatter = JSONFormatter()
        
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='test.py',
            lineno=1,
            msg='Test message',
            args=(),
            exc_info=None
        )
        
        result = formatter.format(record)
        assert 'Test message' in result
        assert 'timestamp' in result
        assert 'level' in result
    
    def test_plain_formatter(self):
        """Test plain formatter."""
        from src.logging_config import PlainFormatter
        formatter = PlainFormatter()
        
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='test.py',
            lineno=1,
            msg='Test message',
            args=(),
            exc_info=None
        )
        
        result = formatter.format(record)
        assert 'Test message' in result
