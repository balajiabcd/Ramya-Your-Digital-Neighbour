# Phase 2: Production Security

## Context
Add security hardening to protect against common web vulnerabilities. Essential for production deployments exposed to the internet.

**Project:** Ramya: Your Digital Neighbour  
**App Name:** Ramya

## Current State
- No security headers
- Basic CORS (none configured)
- In-memory rate limiting (resets on restart)
- Simple session-based auth

## Brief Plan
1. Add Flask-Talisman for security headers (HSTS, CSP, X-Frame-Options, etc.)
2. Configure CORS properly for allowed origins
3. Implement Redis-based rate limiting (persistent, scalable)
4. Add security middleware for request validation
5. Add secure session configuration

---

## Detailed Step-by-Step Implementation

### Step 1: Update requirements.txt

Add Flask-Talisman and additional security dependencies:

```bash
pip install flask-talisman
```

Add to requirements.txt:
```
flask-talisman==1.0.0
```

---

### Step 2: Create Security Configuration Module

Create `src/security_config.py`:

```python
"""
Security configuration for Ramya application.
Phase 2: Production Security
"""

import os
from functools import wraps


# =============================================================================
# Security Headers Configuration (Flask-Talisman)
# =============================================================================

def get_security_headers():
    """
    Get security headers configuration based on environment.
    """
    is_production = os.getenv('APP_ENV') == 'Production'
    
    return {
        'force_https': is_production,
        'force_https_permanent': False,
        'strict_transport_security': 'max-age=31536000; includeSubDomains',
        'content_security_policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self' data:; connect-src 'self' https://openrouter.ai;",
        'content_security_policy_report_uri': None,
        'content_security_policy_report_only': False,
        'content_security_policy_nonce_in': [],
        'x_frame_options': 'DENY',
        'x_xss_protection': '1; mode=block',
        'x_content_type_options': 'nosniff',
        'referrer_policy': 'strict-origin-when-cross-origin',
        'permissions_policy': 'geolocation=(), microphone=(), camera=()',
        'cross_origin_opener_policy': 'same-origin',
        'cross_origin_resource_policy': 'same-origin',
        'cross_origin_embedder_policy': 'require-corp',
    }


def get_cors_config():
    """
    Get CORS configuration.
    """
    allowed_origins = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
    
    if not allowed_origins or allowed_origins == ['']:
        # Default: allow same origin in production
        allowed_origins = ['http://localhost:8080', 'http://127.0.0.1:8080']
    
    return {
        'origins': allowed_origins,
        'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
        'allow_headers': ['Content-Type', 'Authorization', 'X-Requested-With'],
        'expose_headers': ['Content-Length', 'Content-Type'],
        'supports_credentials': True,
        'max_age': 3600,
    }


# =============================================================================
# Rate Limiting Configuration
# =============================================================================

def get_rate_limit_config():
    """
    Get rate limiting configuration.
    """
    return {
        # Chat rate limits
        'chat': {
            'limit': int(os.getenv('RATE_LIMIT_CHAT', '5')),
            'window': int(os.getenv('RATE_LIMIT_CHAT_WINDOW', '60')),
        },
        # TTS rate limits
        'tts': {
            'limit': int(os.getenv('RATE_LIMIT_TTS', '10')),
            'window': int(os.getenv('RATE_LIMIT_TTS_WINDOW', '60')),
        },
        # STT rate limits
        'stt': {
            'limit': int(os.getenv('RATE_LIMIT_STT', '10')),
            'window': int(os.getenv('RATE_LIMIT_STT_WINDOW', '60')),
        },
    }


# =============================================================================
# Session Security Configuration
# =============================================================================

def get_session_config():
    """
    Get session security configuration.
    """
    return {
        'cookie_name': 'ramya_session',
        'cookie_secure': os.getenv('APP_ENV') == 'Production',
        'cookie_httponly': True,
        'cookie_samesite': 'Lax' if os.getenv('APP_ENV') == 'Production' else 'None',
        'permanent_session_lifetime': 3600 * 24 * 7,  # 7 days
    }


# =============================================================================
# IP Blacklist/Whitelist (Future)
# =============================================================================

def get_ip_config():
    """
    Get IP whitelist/blacklist configuration.
    """
    whitelist = os.getenv('IP_WHITELIST', '').split(',')
    blacklist = os.getenv('IP_BLACKLIST', '').split(',')
    
    return {
        'whitelist': [ip.strip() for ip in whitelist if ip.strip()],
        'blacklist': [ip.strip() for ip in blacklist if ip.strip()],
    }
```

---

### Step 3: Create Redis Rate Limiter Module

Create `src/rate_limiter.py`:

```python
"""
Redis-based rate limiter for Ramya.
Phase 2: Production Security
"""

import os
import time
import logging
from typing import Optional, Tuple
import redis

logger = logging.getLogger(__name__)


class RedisRateLimiter:
    """
    Redis-based sliding window rate limiter.
    """
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self._connect()
    
    def _connect(self):
        """Connect to Redis."""
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        
        try:
            self.redis_client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            self.redis_client.ping()
            logger.info("Redis rate limiter connected successfully")
        except redis.ConnectionError as e:
            logger.warning(f"Redis connection failed, falling back to in-memory: {e}")
            self.redis_client = None
        except Exception as e:
            logger.error(f"Unexpected error connecting to Redis: {e}")
            self.redis_client = None
    
    def is_allowed(self, key: str, limit: int, window: int) -> Tuple[bool, int]:
        """
        Check if request is allowed under rate limit.
        
        Args:
            key: Unique identifier (e.g., IP address or user ID)
            limit: Maximum number of requests allowed
            window: Time window in seconds
            
        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        if self.redis_client is None:
            # Fallback to in-memory rate limiter
            return self._in_memory_fallback(key, limit, window)
        
        try:
            current_time = int(time.time())
            window_start = current_time - window
            redis_key = f"ratelimit:{key}"
            
            # Remove old entries outside the window
            self.redis_client.zremrangebyscore(redis_key, 0, window_start)
            
            # Count current requests in window
            current_count = self.redis_client.zcard(redis_key)
            
            if current_count < limit:
                # Add new request
                self.redis_client.zadd(redis_key, {str(current_time): current_time})
                # Set expiry
                self.redis_client.expire(redis_key, window)
                
                return True, limit - current_count - 1
            else:
                return False, 0
                
        except redis.RedisError as e:
            logger.error(f"Redis error in rate limiter: {e}")
            return self._in_memory_fallback(key, limit, window)
    
    def _in_memory_fallback(self, key: str, limit: int, window: int) -> Tuple[bool, int]:
        """
        Fallback to in-memory rate limiting when Redis is unavailable.
        """
        from collections import deque
        import threading
        
        if not hasattr(self, '_memory_store'):
            self._memory_store = {}
            self._lock = threading.Lock()
        
        with self._lock:
            current_time = time.time()
            window_start = current_time - window
            
            if key not in self._memory_store:
                self._memory_store[key] = deque()
            
            # Remove old entries
            while self._memory_store[key] and self._memory_store[key][0] < window_start:
                self._memory_store[key].popleft()
            
            # Check limit
            current_count = len(self._memory_store[key])
            
            if current_count < limit:
                self._memory_store[key].append(current_time)
                return True, limit - current_count - 1
            else:
                return False, 0
    
    def get_remaining(self, key: str, limit: int, window: int) -> int:
        """
        Get remaining requests for a key.
        """
        if self.redis_client is None:
            return limit  # Can't determine without Redis
        
        try:
            current_time = int(time.time())
            window_start = current_time - window
            redis_key = f"ratelimit:{key}"
            
            self.redis_client.zremrangebyscore(redis_key, 0, window_start)
            current_count = self.redis_client.zcard(redis_key)
            
            return max(0, limit - current_count)
        except:
            return limit


# Global rate limiter instance
_rate_limiter: Optional[RedisRateLimiter] = None


def get_rate_limiter() -> RedisRateLimiter:
    """Get or create the rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RedisRateLimiter()
    return _rate_limiter


def check_rate_limit(limit_type: str, identifier: str) -> Tuple[bool, int]:
    """
    Check rate limit for a given type and identifier.
    
    Args:
        limit_type: Type of limit ('chat', 'tts', 'stt')
        identifier: IP address or user ID
        
    Returns:
        Tuple of (is_allowed, remaining_requests)
    """
    from src.security_config import get_rate_limit_config
    
    config = get_rate_limit_config()
    rate_config = config.get(limit_type, {'limit': 5, 'window': 60})
    
    limiter = get_rate_limiter()
    return limiter.is_allowed(
        f"{limit_type}:{identifier}",
        rate_config['limit'],
        rate_config['window']
    )
```

---

### Step 4: Update app.py with Security Middleware

Modify `app.py`:

```python
import os
from dotenv import load_dotenv

from src.d_security_utils import validate_api_key

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")
validate_api_key(api_key)

from flask import Flask

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
app.secret_key = os.getenv("SECRET_KEY", "default-secret-key")


# =============================================================================
# Phase 2: Security Configuration
# =============================================================================

# Session security
app.config.update(
    SESSION_COOKIE_SECURE=os.getenv('APP_ENV') == 'Production',
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax' if os.getenv('APP_ENV') == 'Production' else 'None',
)

# Security Headers (Flask-Talisman)
try:
    from flask_talisman import Talisman
    from src.security_config import get_security_headers, get_cors_config
    
    security_headers = get_security_headers()
    cors_config = get_cors_config()
    
    Talisman(
        app,
        force_https=security_headers['force_https'],
        strict_transport_security=security_headers['strict_transport_security'],
        content_security_policy=security_headers['content_security_policy'],
        x_frame_options=security_headers['x_frame_options'],
        x_xss_protection=security_headers['x_xss_protection'],
        x_content_type_options=security_headers['x_content_type_options'],
        referrer_policy=security_headers['referrer_policy'],
        permissions_policy=security_headers['permissions_policy'],
    )
    print("Flask-Talisman security headers enabled")
    
except ImportError:
    print("WARNING: flask-talisman not installed. Run: pip install flask-talisman")


@app.context_processor
def override_url_for():
    from src.j_utils import dated_url_for
    return dict(url_for=dated_url_for)


from src.routes.k_auth import auth_bp
from src.routes.l_home import home_bp
from src.routes.m_chat import chat_bp
from src.routes.n_tts import tts_bp
from src.routes.o_stt import stt_bp
from src.p_error_handlers import errors_bp


app.register_blueprint(auth_bp, url_prefix='')
app.register_blueprint(home_bp, url_prefix='')
app.register_blueprint(chat_bp, url_prefix='')
app.register_blueprint(tts_bp, url_prefix='')
app.register_blueprint(stt_bp, url_prefix='')
app.register_blueprint(errors_bp)


if __name__ == '__main__':
    is_debug = os.getenv('APP_ENV', 'Development') == 'Development'
    app.run(debug=is_debug, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
```

---

### Step 5: Update Rate Limiting in Routes

#### 5.1 Update chat route (`src/routes/m_chat.py`)

```python
from flask import request, jsonify, Response, Blueprint
from src.d_security_utils import sanitize_string, detect_injection
from src.f_auth import login_required
from src.j_utils import get_bot

# Use Redis-based rate limiter
try:
    from src.rate_limiter import check_rate_limit
    USE_REDIS_RATELIMIT = True
except ImportError:
    USE_REDIS_RATELIMIT = False
    from src.d_security_utils import RateLimiter


chat_bp = Blueprint('chat', __name__)

# Initialize rate limiter
if USE_REDIS_RATELIMIT:
    pass  # Using Redis-based rate limiter
else:
    limiter = RateLimiter(limit=5, window=60)


@chat_bp.route('/send_message', methods=['POST'])
@login_required
def send_message():
    """Send a message and get AI response."""
    ip = request.remote_addr or "unknown"
    
    # Use Redis-based rate limiting
    if USE_REDIS_RATELIMIT:
        is_allowed, remaining = check_rate_limit('chat', ip)
        if not is_allowed:
            return jsonify({
                "status": "error", 
                "message": "Whoa there! You're chatting too fast. Please wait a minute before sending more messages."
            }), 429
    else:
        # Fallback to in-memory
        if not limiter.is_allowed(ip):
            return jsonify({
                "status": "error", 
                "message": "Whoa there! You're chatting too fast. Please wait a minute before sending more messages."
            }), 429

    # ... rest of the code
```

#### 5.2 Update TTS route (`src/routes/n_tts.py`)

Similar changes to use Redis-based rate limiting for TTS endpoints.

#### 5.3 Update STT route (`src/routes/o_stt.py`)

Similar changes to use Redis-based rate limiting for STT endpoints.

---

### Step 6: Update docker-compose.yml with Redis

Uncomment Redis service in `docker-compose.yml`:

```yaml
  redis:
    image: redis:7-alpine
    container_name: ramya-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - ramya-network
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

# Add to volumes:
  redis_data:
    driver: local
```

Add environment variable to Ramya service:
```yaml
    environment:
      - REDIS_URL=redis://redis:6379/0
```

---

### Step 7: Add Security Environment Variables

Update `.env`:

```env
# Security
APP_ENV=Production
SECRET_KEY=your-production-secret-key-min-32-characters-long

# CORS (comma-separated origins)
CORS_ALLOWED_ORIGINS=http://localhost:8080,https://yourdomain.com

# Rate Limiting
RATE_LIMIT_CHAT=5
RATE_LIMIT_CHAT_WINDOW=60
RATE_LIMIT_TTS=10
RATE_LIMIT_TTS_WINDOW=60
RATE_LIMIT_STT=10
RATE_LIMIT_STT_WINDOW=60

# Redis
REDIS_URL=redis://redis:6379/0

# Paths
CHROMADB_PATH=/app/ramya_memory_db
LOG_DIR=/app/logs
PORT=8080
```

---

### Step 8: Test the Security Implementation

#### 8.1 Test Headers
```bash
curl -I http://localhost:8080/
```

Expected headers:
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`

#### 8.2 Test Rate Limiting
```bash
# Send multiple requests rapidly
for i in {1..10}; do curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080/send_message -X POST -H "Content-Type: application/json" -d '{"message":"test"}'; done
```

Should return 429 after limit exceeded.

#### 8.3 Test Redis Connection
```bash
docker exec -it ramya-redis redis-cli ping
# Should return: PONG
```

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `src/security_config.py` | Create | Security configuration module |
| `src/rate_limiter.py` | Create | Redis-based rate limiter |
| `app.py` | Modify | Add Flask-Talisman and session config |
| `src/routes/m_chat.py` | Modify | Use Redis rate limiter |
| `src/routes/n_tts.py` | Modify | Use Redis rate limiter |
| `src/routes/o_stt.py` | Modify | Use Redis rate limiter |
| `docker-compose.yml` | Modify | Uncomment Redis service |
| `.env` | Modify | Add security env vars |
| `requirements.txt` | Modify | Add flask-talisman |

---

## Verification Checklist

- [ ] Flask-Talisman installed and working
- [ ] Security headers present in responses
- [ ] CORS configured for allowed origins
- [ ] Redis rate limiting working
- [ ] Fallback to in-memory when Redis unavailable
- [ ] Session cookies secure in production
- [ ] Rate limit headers included in responses (`X-RateLimit-Remaining`)
- [ ] Docker Compose includes Redis service

---

## Troubleshooting

### Issue: Flask-Talisman blocks static files
**Solution:** Add static file URL prefix to CSP:
```python
content_security_policy="default-src 'self'; ...",
content_security_policy_default_src_self=True,
static_folder='static',
static_url_path='/static',
```

### Issue: CORS preflight failing
**Solution:** Ensure OPTIONS method is allowed in CORS config.

### Issue: Redis connection refused
**Solution:** Check Redis is running and `REDIS_URL` is correct.

---

## Next Phase

After completing Phase 2, proceed to **Phase 3: Authentication System** to add:
- Password hashing with bcrypt
- Secure session management
- User registration
