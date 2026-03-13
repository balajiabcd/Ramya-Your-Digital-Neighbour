"""
Error handlers for Ramya.
Phase 5: Logging & Error Handling
"""

import logging
import traceback
from flask import jsonify, request, Blueprint
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)

errors_bp = Blueprint('errors', __name__)


@errors_bp.after_request
def add_security_headers(response):
    """Inject security headers into every response."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response


@errors_bp.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request."""
    logger.warning(f"400 Bad Request: {request.path} - {str(error)}")
    return jsonify({
        "status": "error",
        "message": "Bad request. Please check your input.",
        "code": "BAD_REQUEST"
    }), 400


@errors_bp.errorhandler(401)
def unauthorized(error):
    """Handle 401 Unauthorized."""
    logger.warning(f"401 Unauthorized: {request.path}")
    return jsonify({
        "status": "error",
        "message": "Authentication required. Please login.",
        "code": "UNAUTHORIZED"
    }), 401


@errors_bp.errorhandler(403)
def forbidden(error):
    """Handle 403 Forbidden."""
    logger.warning(f"403 Forbidden: {request.path}")
    return jsonify({
        "status": "error",
        "message": "You don't have permission to access this resource.",
        "code": "FORBIDDEN"
    }), 403


@errors_bp.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    logger.info(f"404 Not Found: {request.path}")
    return jsonify({
        "status": "error",
        "message": "The requested resource was not found.",
        "code": "NOT_FOUND"
    }), 404


@errors_bp.errorhandler(429)
def rate_limited(error):
    """Handle 429 Rate Limited."""
    logger.warning(f"429 Rate Limited: {request.path} - {request.remote_addr}")
    return jsonify({
        "status": "error",
        "message": "Too many requests. Please slow down.",
        "code": "RATE_LIMITED"
    }), 429


@errors_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server Error."""
    logger.error(f"500 Internal Error: {request.path} - {str(error)}", exc_info=True)
    return jsonify({
        "status": "error",
        "message": "An internal error occurred. Please try again later.",
        "code": "INTERNAL_ERROR"
    }), 500


@errors_bp.errorhandler(503)
def service_unavailable(error):
    """Handle 503 Service Unavailable."""
    logger.error(f"503 Service Unavailable: {request.path}")
    return jsonify({
        "status": "error",
        "message": "Service temporarily unavailable. Please try again later.",
        "code": "SERVICE_UNAVAILABLE"
    }), 503


@errors_bp.errorhandler(HTTPException)
def handle_http_exception(error):
    """Handle generic HTTP exceptions."""
    logger.warning(f"HTTP Exception: {error.code} - {error.description}")
    return jsonify({
        "status": "error",
        "message": error.description,
        "code": error.name.upper().replace(" ", "_")
    }), error.code


@errors_bp.errorhandler(Exception)
def handle_global_exception(error):
    """Catch-all error handler for uncaught exceptions."""
    logger.error(
        f"Unhandled Exception: {request.path} - {str(error)}",
        exc_info=traceback.format_exc()
    )
    
    return jsonify({
        "status": "error",
        "message": "An unexpected error occurred.",
        "code": "INTERNAL_ERROR"
    }), 500
