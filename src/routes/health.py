"""
Health check and monitoring routes for Ramya.
Phase 6: Health Monitoring
"""

import time
import psutil
import logging
from flask import Blueprint, jsonify, request, g
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST

logger = logging.getLogger(__name__)

health_bp = Blueprint('health', __name__)

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Gauge('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
ACTIVE_USERS = Gauge('active_users', 'Number of active users')
SYSTEM_CPU = Gauge('system_cpu_percent', 'System CPU usage percent')
SYSTEM_MEMORY = Gauge('system_memory_percent', 'System memory usage percent')
CHROMA_DB_CONNECTED = Gauge('chromadb_connected', 'ChromaDB connection status')
REDIS_CONNECTED = Gauge('redis_connected', 'Redis connection status')


@health_bp.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": time.time()
    }), 200


@health_bp.route('/health/live', methods=['GET'])
def liveness():
    """Kubernetes liveness probe."""
    return jsonify({"status": "alive"}), 200


@health_bp.route('/health/ready', methods=['GET'])
def readiness():
    """Kubernetes readiness probe."""
    checks = {}
    overall_healthy = True
    
    try:
        import chromadb
        client = chromadb.PersistentClient()
        client.heartbeat()
        CHROMA_DB_CONNECTED.set(1)
        checks["chromadb"] = "ok"
    except Exception as e:
        CHROMA_DB_CONNECTED.set(0)
        checks["chromadb"] = f"error: {str(e)}"
        overall_healthy = False
    
    try:
        from src.rate_limiter import get_rate_limiter
        limiter = get_rate_limiter()
        if limiter.redis_client:
            limiter.redis_client.ping()
            REDIS_CONNECTED.set(1)
            checks["redis"] = "ok"
        else:
            REDIS_CONNECTED.set(0)
            checks["redis"] = "not_configured"
    except Exception as e:
        REDIS_CONNECTED.set(0)
        checks["redis"] = f"error: {str(e)}"
    
    status_code = 200 if overall_healthy else 503
    
    return jsonify({
        "status": "ready" if overall_healthy else "not_ready",
        "checks": checks
    }), status_code


@health_bp.route('/health/status', methods=['GET'])
def detailed_status():
    """Detailed status endpoint with system info."""
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    
    SYSTEM_CPU.set(cpu_percent)
    SYSTEM_MEMORY.set(memory.percent)
    
    import os
    try:
        uptime = time.time() - psutil.Process(os.getpid()).create_time()
    except:
        uptime = 0
    
    return jsonify({
        "status": "healthy",
        "application": {
            "name": "Ramya",
            "version": "1.0.0",
            "uptime_seconds": uptime
        },
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_mb": memory.available / (1024 * 1024)
        }
    }), 200


@health_bp.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus metrics endpoint."""
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    
    SYSTEM_CPU.set(cpu_percent)
    SYSTEM_MEMORY.set(memory.percent)
    
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}


def track_request_metrics(response):
    """Track request metrics."""
    try:
        endpoint = request.path
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=endpoint,
            status=response.status_code
        ).inc()
    except:
        pass
    return response
