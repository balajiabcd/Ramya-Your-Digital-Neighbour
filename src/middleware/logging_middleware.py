"""
Logging middleware for request/response tracking.
Phase 5: Logging & Error Handling
"""

import time
import uuid
import logging
from flask import Flask, g, session

logger = logging.getLogger(__name__)


def setup_logging_middleware(app: Flask):
    """Setup logging middleware for the Flask app."""
    
    @app.before_request
    def before_request():
        """Generate request ID and track start time."""
        g.request_id = str(uuid.uuid4())[:8]
        g.start_time = time.time()
        
        user_id = None
        if 'user' in session:
            user_id = session.get('user', {}).get('username') or session.get('user', {}).get('email')
        
        extra = {
            "request_id": g.request_id,
            "ip": getattr(g, 'request', None) and getattr(g.request, 'remote_addr', 'unknown'),
            "method": getattr(g, 'request', None) and getattr(g.request, 'method', 'unknown'),
            "path": getattr(g, 'request', None) and getattr(g.request, 'path', 'unknown'),
            "user": user_id,
        }
        
        from flask import request
        logger.info(
            f"Request started: {request.method} {request.path}",
            extra={
                "request_id": g.request_id,
                "ip": request.remote_addr,
                "method": request.method,
                "path": request.path,
                "user": user_id,
            }
        )
    
    @app.after_request
    def after_request(response):
        """Log response with duration."""
        if hasattr(g, 'request_id'):
            duration = (time.time() - g.start_time) * 1000
            
            user_id = None
            if 'user' in session:
                user_id = session.get('user', {}).get('username') or session.get('user', {}).get('email')
            
            from flask import request
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
            
            response.headers['X-Request-ID'] = g.request_id
        
        return response
    
    @app.teardown_request
    def teardown_request(exception=None):
        """Log any exceptions that occurred during request."""
        if exception:
            user_id = None
            if 'user' in session:
                user_id = session.get('user', {}).get('username') or session.get('user', {}).get('email')
            
            from flask import request
            logger.error(
                f"Request error: {request.method} {request.path} - {str(exception)}",
                exc_info=exception,
                extra={
                    "request_id": g.get('request_id', 'unknown'),
                    "ip": request.remote_addr,
                    "method": request.method,
                    "path": request.path,
                    "user": user_id,
                }
            )
