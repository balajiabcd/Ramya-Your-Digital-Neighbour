# Phase 5: Logging & Error Handling

## Context
Add structured logging and comprehensive error handling for better debugging, monitoring, and user experience in production.

**Project:** Ramya: Your Digital Neighbour  
**App Name:** Ramya

## Current State
- Basic print statements for logging
- No structured logging format
- Simple error handlers in `src/p_error_handlers.py`
- No request ID tracking

## Brief Plan
1. Implement structured JSON logging
2. Add request ID tracking (for log correlation)
3. Create comprehensive error handlers (4xx, 5xx)
4. Create comprehensive log system for error records
5. Add logging middleware for request/response tracking
6. Configure log levels per environment

---

## Detailed Step-by-Step Implementation

### Step 1: Create Logging Configuration

Create `src/logging_config.py`:

```python
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
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
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
    """
    Setup logging for the application.
    
    Args:
        app_env: Application environment (Development, Staging, Production)
        log_dir: Directory for log files
    
    Returns:
        Configured logger
    """
    # Create logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if app_env == "Development" else logging.INFO)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if app_env == "Development" else logging.INFO)
    
    if app_env == "Development":
        console_handler.setFormatter(PlainFormatter())
    else:
        console_handler.setFormatter(JSONFormatter())
    
    logger.addHandler(console_handler)
    
    # File handler (rotating)
    log_file = os.path.join(log_dir, "ramya.log")
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG if app_env == "Development" else logging.INFO)
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)
    
    # Error file handler
    error_file = os.path.join(log_dir, "ramya_errors.log")
    error_handler = RotatingFileHandler(
        error_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(JSONFormatter())
    logger.addHandler(error_handler)
    
    # Set levels for third-party loggers
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(name)
```

---

### Step 2: Create Logging Middleware

Create `src/middleware/logging_middleware.py`:

```python
"""
Logging middleware for request/response tracking.
Phase 5: Logging & Error Handling
"""

import time
import uuid
import logging
from flask import Flask, request, g, session
from typing import Callable

logger = logging.getLogger(__name__)


def setup_logging_middleware(app: Flask):
    """Setup logging middleware for the Flask app."""
    
    @app.before_request
    def before_request():
        """Generate request ID and track start time."""
        g.request_id = str(uuid.uuid4())[:8]
        g.start_time = time.time()
        
        # Get user if logged in
        user_id = None
        if 'user' in session:
            user_id = session.get('user', {}).get('username') or session.get('user', {}).get('email')
        
        # Log request
        extra = {
            "request_id": g.request_id,
            "ip": request.remote_addr,
            "method": request.method,
            "path": request.path,
            "user": user_id,
        }
        
        logger.info(
            f"Request started: {request.method} {request.path}",
            extra=extra
        )
    
    @app.after_request
    def after_request(response):
        """Log response with duration."""
        if hasattr(g, 'request_id'):
            duration = (time.time() - g.start_time) * 1000  # ms
            
            user_id = None
            if 'user' in session:
                user_id = session.get('user', {}).get('username') or session.get('user', {}).get('email')
            
            extra = {
                "request_id": g.request_id,
                "ip": request.remote_addr,
                "method": request.method,
                "path": request.path,
                "status_code": response.status_code,
                "duration": round(duration, 2),
                "user": user_id,
            }
            
            log_level = logging.INFO if response.status_code < 400 else logging.WARNING
            
            logger.log(
                log_level,
                f"Request completed: {request.method} {request.path} - {response.status_code} ({duration:.2f}ms)",
                extra=extra
            )
        
        # Add request ID to response headers
        if hasattr(g, 'request_id'):
            response.headers['X-Request-ID'] = g.request_id
        
        return response
    
    @app.teardown_request
    def teardown_request(exception=None):
        """Log any exceptions that occurred during request."""
        if exception:
            user_id = None
            if 'user' in session:
                user_id = session.get('user', {}).get('username') or session.get('user', {}).get('email')
            
            extra = {
                "request_id": g.get('request_id', 'unknown'),
                "ip": request.remote_addr,
                "method": request.method,
                "path": request.path,
                "user": user_id,
            }
            
            logger.error(
                f"Request error: {request.method} {request.path} - {str(exception)}",
                exc_info=exception,
                extra=extra
            )
```

---

### Step 3: Update Error Handlers

Update `src/p_error_handlers.py`:

```python
"""
Error handlers for Ramya.
Phase 5: Logging & Error Handling
"""

import logging
import traceback
from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


def setup_error_handlers(app: Flask):
    """Setup comprehensive error handlers."""
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request."""
        logger.warning(f"400 Bad Request: {request.path} - {str(error)}")
        return jsonify({
            "status": "error",
            "message": "Bad request. Please check your input.",
            "code": "BAD_REQUEST"
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Handle 401 Unauthorized."""
        logger.warning(f"401 Unauthorized: {request.path}")
        return jsonify({
            "status": "error",
            "message": "Authentication required. Please login.",
            "code": "UNAUTHORIZED"
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden."""
        logger.warning(f"403 Forbidden: {request.path}")
        return jsonify({
            "status": "error",
            "message": "You don't have permission to access this resource.",
            "code": "FORBIDDEN"
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found."""
        logger.info(f"404 Not Found: {request.path}")
        return jsonify({
            "status": "error",
            "message": "The requested resource was not found.",
            "code": "NOT_FOUND"
        }), 404
    
    @app.errorhandler(429)
    def rate_limited(error):
        """Handle 429 Rate Limited."""
        logger.warning(f"429 Rate Limited: {request.path} - {request.remote_addr}")
        return jsonify({
            "status": "error",
            "message": "Too many requests. Please slow down.",
            "code": "RATE_LIMITED"
        }), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server Error."""
        logger.error(f"500 Internal Error: {request.path} - {str(error)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "An internal error occurred. Please try again later.",
            "code": "INTERNAL_ERROR"
        }), 500
    
    @app.errorhandler(503)
    def service_unavailable(error):
        """Handle 503 Service Unavailable."""
        logger.error(f"503 Service Unavailable: {request.path}")
        return jsonify({
            "status": "error",
            "message": "Service temporarily unavailable. Please try again later.",
            "code": "SERVICE_UNAVAILABLE"
        }), 503
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Handle generic HTTP exceptions."""
        logger.warning(f"HTTP Exception: {error.code} - {error.description}")
        return jsonify({
            "status": "error",
            "message": error.description,
            "code": error.name.upper().replace(" ", "_")
        }), error.code
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle unhandled exceptions."""
        logger.error(
            f"Unhandled Exception: {request.path} - {str(error)}",
            exc_info=traceback.format_exc()
        )
        
        # Don't expose internal errors in production
        return jsonify({
            "status": "error",
            "message": "An unexpected error occurred.",
            "code": "INTERNAL_ERROR"
        }), 500
```

---

### Step 4: Update app.py

Add logging setup to app.py:

```python
# ... existing imports ...

# Setup logging
from src.config import get_config
config = get_config()

from src.logging_config import setup_logging
logger = setup_logging(app_env=config.env, log_dir=config.paths.log_dir)

# Setup logging middleware
from src.middleware.logging_middleware import setup_logging_middleware
setup_logging_middleware(app)

# ... rest of the code ...
```

---

### Step 5: Create middleware __init__.py

Create `src/middleware/__init__.py`:

```python
"""Middleware package for Ramya."""
from src.middleware.logging_middleware import setup_logging_middleware

__all__ = ['setup_logging_middleware']
```

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `src/logging_config.py` | Create | Logging configuration |
| `src/middleware/__init__.py` | Create | Middleware package |
| `src/middleware/logging_middleware.py` | Create | Request/response logging |
| `src/p_error_handlers.py` | Modify | Comprehensive error handlers |
| `app.py` | Modify | Add logging setup |

---

## Verification Checklist

- [ ] JSON logs in production
- [ ] Plain text logs in development
- [ ] Request ID in all logs
- [ ] User ID in logs when logged in
- [ ] Response duration tracked
- [ ] All error codes handled (400, 401, 403, 404, 429, 500, 503)
- [ ] Separate error log file

---

## Next Phase

After completing Phase 5, proceed to **Phase 6: Health Monitoring** to add:
- /health endpoint
- /metrics endpoint
- Startup health checks
