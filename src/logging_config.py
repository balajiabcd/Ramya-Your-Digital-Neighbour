"""
Logging configuration for Ramya.
Phase 5: Logging & Error Handling
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Any, Dict
from logging.handlers import RotatingFileHandler


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "user"):
            log_data["user"] = record.user
        if hasattr(record, "ip"):
            log_data["ip"] = record.ip
        if hasattr(record, "path"):
            log_data["path"] = record.path
        if hasattr(record, "method"):
            log_data["method"] = record.method
        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code
        if hasattr(record, "duration"):
            log_data["duration_ms"] = record.duration
        
        return json.dumps(log_data)


class PlainFormatter(logging.Formatter):
    """Plain text formatter for development."""
    
    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp}] {record.levelname:8} {record.name:20} {record.getMessage()}"


def setup_logging(app_env: str = "Development", log_dir: str = "logs") -> logging.Logger:
    """Setup logging for the application."""
    os.makedirs(log_dir, exist_ok=True)
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if app_env == "Development" else logging.INFO)
    logger.handlers.clear()
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if app_env == "Development" else logging.INFO)
    
    if app_env == "Development":
        console_handler.setFormatter(PlainFormatter())
    else:
        console_handler.setFormatter(JSONFormatter())
    
    logger.addHandler(console_handler)
    
    log_file = os.path.join(log_dir, "ramya.log")
    file_handler = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5)
    file_handler.setLevel(logging.DEBUG if app_env == "Development" else logging.INFO)
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)
    
    error_file = os.path.join(log_dir, "ramya_errors.log")
    error_handler = RotatingFileHandler(error_file, maxBytes=10 * 1024 * 1024, backupCount=5)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(JSONFormatter())
    logger.addHandler(error_handler)
    
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(name)
