# Phase 6: Health Monitoring

## Context
Add health check endpoints and monitoring capabilities for production deployment and Kubernetes integration.

**Project:** Ramya: Your Digital Neighbour  
**App Name:** Ramya

## Current State
- Basic health check in `RamyaBot.check_health()` method (not exposed as endpoint)
- No Prometheus metrics endpoint
- No startup health validation

## Brief Plan
1. Create `/health` endpoint for liveness/readiness probes
2. Add `/metrics` endpoint (Prometheus format)
3. Implement startup health checks
4. Add system metrics (CPU, memory, request stats)
5. Add structured status response

---

## Detailed Step-by-Step Implementation

### Step 1: Create Health Routes

Create `src/routes/health.py`:

```python
"""
Health check and monitoring routes for Ramya.
Phase 6: Health Monitoring
"""

import time
import psutil
import logging
from flask import Blueprint, jsonify, request
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST

logger = logging.getLogger(__name__)

health_bp = Blueprint('health', __name__)

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Gauge('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
ACTIVE_USERS = Gauge('active_users', 'Number of active users')
SYSTEM_CPU = Gauge('system_cpu_percent', 'System CPU usage percent')
SYSTEM_MEMORY = Gauge('system_memory_percent', 'System memory usage percent')
CHROMA_DB_CONNECTED = Gauge('chromadb_connected', 'ChromaDB connection status')
REDIS_CONNECTED = Gauge('redis_connected', 'Redis connection status')


@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Basic health check endpoint.
    Returns 200 if healthy, 503 if not.
    """
    return jsonify({
        "status": "healthy",
        "timestamp": time.time()
    }), 200


@health_bp.route('/health/live', methods=['GET'])
def liveness():
    """
    Kubernetes liveness probe.
    Returns 200 if app is running.
    """
    return jsonify({"status": "alive"}), 200


@health_bp.route('/health/ready', methods=['GET'])
def readiness():
    """
    Kubernetes readiness probe.
    Returns 200 if app can serve traffic.
    """
    checks = {}
    overall_healthy = True
    
    # Check ChromaDB
    try:
        from src.a_ai_engine import RamyaBot
        bot = RamyaBot(api_key="", user_email="healthcheck")
        chroma_ok = bot.check_health()
        CHROMA_DB_CONNECTED.set(1 if chroma_ok else 0)
        checks["chromadb"] = "ok" if chroma_ok else "error"
        if not chroma_ok:
            overall_healthy = False
    except Exception as e:
        CHROMA_DB_CONNECTED.set(0)
        checks["chromadb"] = f"error: {str(e)}"
        overall_healthy = False
    
    # Check Redis
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
    """
    Detailed status endpoint with system info.
    """
    # System metrics
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    
    SYSTEM_CPU.set(cpu_percent)
    SYSTEM_MEMORY.set(memory.percent)
    
    # Get app uptime
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
        },
        "services": {
            "chromadb": "ok",
            "redis": "ok"
        }
    }), 200


@health_bp.route('/metrics', methods=['GET'])
def metrics():
    """
    Prometheus metrics endpoint.
    """
    # Update system metrics
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    
    SYSTEM_CPU.set(cpu_percent)
    SYSTEM_MEMORY.set(memory.percent)
    
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}


def track_request_metrics(response):
    """Track request metrics."""
    try:
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.path,
            status=response.status_code
        ).inc()
    except:
        pass
    return response
```

---

### Step 2: Update app.py

Add health routes to app.py:

```python
# Add health blueprint
from src.routes.health import health_bp
app.register_blueprint(health_bp, url_prefix='')

# Register metrics middleware
from src.routes.health import track_request_metrics
after_request(track_request_metrics)
```

---

### Step 3: Update Requirements

Add to requirements.txt:
```
prometheus-client==0.24.1
psutil==5.9.4
```

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `src/routes/health.py` | Create | Health endpoints and metrics |
| `app.py` | Modify | Register health blueprint |

---

## Endpoints

| Endpoint | Purpose |
|----------|---------|
| `/health` | Basic liveness |
| `/health/live` | Kubernetes liveness |
| `/health/ready` | Kubernetes readiness |
| `/health/status` | Detailed status |
| `/metrics` | Prometheus metrics |

---

## Verification Checklist

- [ ] /health returns 200
- [ ] /health/live returns 200
- [ ] /health/ready checks dependencies
- [ ] /health/status returns system info
- [ ] /metrics returns Prometheus format
- [ ] Metrics track HTTP requests

---

## Next Phase

After completing Phase 6, proceed to **Phase 7: Deployment Checklist** to create production deployment documentation.
