# Phase 4: Environment Configuration

## Context
Implement environment-based configuration management to support different deployment environments (dev, staging, production) with proper secrets handling.

**Project:** Ramya: Your Digital Neighbour  
**App Name:** Ramya

## Current State
- Configuration scattered across .env, app.py, and individual modules
- No formal config validation on startup
- Secrets mixed with configuration code
- No environment-based settings

## Brief Plan
1. Create `config.py` with config classes (Development, Staging, Production)
2. Add environment variable validation on startup
3. Separate secrets from configuration
4. Add configuration for third-party services (OpenRouter, etc.)
5. Add startup validation to fail fast on missing required configs

---

## Detailed Step-by-Step Implementation

### Step 1: Create config.py

Create `src/config.py`:

```python
"""
Configuration management for Ramya.
Phase 4: Environment Configuration
"""

import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


class ConfigError(Exception):
    """Configuration error exception."""
    pass


@dataclass
class SecurityConfig:
    """Security configuration."""
    secret_key: str = ""
    session_cookie_secure: bool = True
    session_cookie_httponly: bool = True
    session_cookie_samesite: str = "Lax"
    session_lifetime: int = 3600 * 24 * 7  # 7 days
    
    # Rate limiting
    rate_limit_chat: int = 5
    rate_limit_chat_window: int = 60
    rate_limit_tts: int = 10
    rate_limit_tts_window: int = 60
    rate_limit_stt: int = 10
    rate_limit_stt_window: int = 60
    
    # CORS
    cors_allowed_origins: List[str] = field(default_factory=lambda: ["http://localhost:8080"])


@dataclass
class APIConfig:
    """API configuration."""
    openrouter_api_key: str = ""
    google_client_id: str = ""
    google_client_secret: str = ""
    redis_url: str = "redis://localhost:6379/0"


@dataclass
class PathsConfig:
    """Paths configuration."""
    chromadb_path: str = "ramya_memory_db"
    log_dir: str = "logs"
    log_file_name: str = "ramya.log"
    audio_dir: str = "static/audio"


@dataclass
class ModelConfig:
    """AI Model configuration."""
    model_ranking: str = ""
    default_model: str = "meta-llama/llama-3.3-70b-instruct:free"


@dataclass
class AppConfig:
    """Main application configuration."""
    env: str = "Development"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8080
    max_content_length: int = 16 * 1024 * 1024  # 16MB
    
    # Sub-configs
    security: SecurityConfig = field(default_factory=SecurityConfig)
    api: APIConfig = field(default_factory=APIConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    models: ModelConfig = field(default_factory=ModelConfig)
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Create config from environment variables."""
        env = os.getenv('APP_ENV', 'Development').lower()
        
        if env not in ['development', 'staging', 'production']:
            raise ConfigError(f"Invalid APP_ENV: {env}. Must be development, staging, or production")
        
        debug = env == 'development'
        
        # Get secret key
        secret_key = os.getenv('SECRET_KEY', '')
        if env == 'production' and not secret_key:
            raise ConfigError("SECRET_KEY is required in production")
        if not secret_key:
            secret_key = "dev-secret-key-change-in-production"
        
        # Parse CORS origins
        cors_origins = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
        cors_origins = [o.strip() for o in cors_origins if o.strip()]
        if not cors_origins:
            cors_origins = ["http://localhost:8080", "http://127.0.0.1:8080"]
        
        # Get API key
        api_key = os.getenv('OPENROUTER_API_KEY', '')
        if not api_key:
            if env == 'production':
                raise ConfigError("OPENROUTER_API_KEY is required in production")
        
        # Security config
        security = SecurityConfig(
            secret_key=secret_key,
            session_cookie_secure=env == 'production',
            session_cookie_httponly=True,
            session_cookie_samesite='Lax' if env == 'production' else 'None',
            session_lifetime=int(os.getenv('SESSION_LIFETIME', str(3600 * 24 * 7))),
            rate_limit_chat=int(os.getenv('RATE_LIMIT_CHAT', '5')),
            rate_limit_chat_window=int(os.getenv('RATE_LIMIT_CHAT_WINDOW', '60')),
            rate_limit_tts=int(os.getenv('RATE_LIMIT_TTS', '10')),
            rate_limit_tts_window=int(os.getenv('RATE_LIMIT_TTS_WINDOW', '60')),
            rate_limit_stt=int(os.getenv('RATE_LIMIT_STT', '10')),
            rate_limit_stt_window=int(os.getenv('RATE_LIMIT_STT_WINDOW', '60')),
            cors_allowed_origins=cors_origins,
        )
        
        # API config
        api = APIConfig(
            openrouter_api_key=api_key,
            google_client_id=os.getenv('GOOGLE_CLIENT_ID', ''),
            google_client_secret=os.getenv('GOOGLE_CLIENT_SECRET', ''),
            redis_url=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
        )
        
        # Paths config
        paths = PathsConfig(
            chromadb_path=os.getenv('CHROMADB_PATH', 'ramya_memory_db'),
            log_dir=os.getenv('LOG_DIR', 'logs'),
            log_file_name=os.getenv('LOG_FILE_NAME', 'ramya.log'),
            audio_dir=os.getenv('AUDIO_DIR', 'static/audio'),
        )
        
        # Model config
        model_ranking = os.getenv('MODEL_RANKING', '{}')
        
        models = ModelConfig(
            model_ranking=model_ranking,
            default_model=os.getenv('DEFAULT_MODEL', 'meta-llama/llama-3.3-70b-instruct:free'),
        )
        
        return cls(
            env=env.capitalize(),
            debug=debug,
            host=os.getenv('HOST', '0.0.0.0'),
            port=int(os.getenv('PORT', '8080')),
            max_content_length=int(os.getenv('MAX_CONTENT_LENGTH', str(16 * 1024 * 1024))),
            security=security,
            api=api,
            paths=paths,
            models=models,
        )
    
    def validate(self) -> List[str]:
        """
        Validate configuration.
        Returns list of warnings (empty if all valid).
        """
        warnings = []
        
        if self.env == 'Production':
            if len(self.security.secret_key) < 32:
                warnings.append("SECRET_KEY should be at least 32 characters in production")
            
            if self.security.cors_allowed_origins == ["http://localhost:8080"]:
                warnings.append("CORS_ALLOWED_ORIGINS not set for production")
        
        if not self.api.openrouter_api_key:
            warnings.append("OPENROUTER_API_KEY not set - AI features will not work")
        
        return warnings


# Global config instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get or create the global config instance."""
    global _config
    if _config is None:
        _config = AppConfig.from_env()
    return _config


def reset_config():
    """Reset config instance (mainly for testing)."""
    global _config
    _config = None


def validate_config() -> None:
    """
    Validate configuration on startup.
    Raises ConfigError if critical issues found.
    """
    config = get_config()
    
    # Critical checks
    if config.env == 'Production':
        if not config.security.secret_key or config.security.secret_key == "dev-secret-key-change-in-production":
            raise ConfigError("SECRET_KEY must be changed in production")
        
        if not config.api.openrouter_api_key:
            raise ConfigError("OPENROUTER_API_KEY is required in production")
    
    # Warnings
    warnings = config.validate()
    for warning in warnings:
        print(f"CONFIG WARNING: {warning}")
```

---

### Step 2: Update app.py to use config

Replace the beginning of app.py:

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Validate API key first
from src.d_security_utils import validate_api_key
from src.config import get_config, validate_config, ConfigError
import sys

# Initialize and validate config
try:
    config = get_config()
    validate_config()
except ConfigError as e:
    print(f"CONFIG ERROR: {e}")
    sys.exit(1)

api_key = os.getenv("OPENROUTER_API_KEY")
validate_api_key(api_key)

from flask import Flask

app = Flask(__name__)

# Apply config to Flask app
app.config['SECRET_KEY'] = config.security.secret_key
app.config['MAX_CONTENT_LENGTH'] = config.max_content_length
app.config['SESSION_COOKIE_SECURE'] = config.security.session_cookie_secure
app.config['SESSION_COOKIE_HTTPONLY'] = config.security.session_cookie_httponly
app.config['SESSION_COOKIE_SAMESITE'] = config.security.session_cookie_samesite


@app.context_processor
def override_url_for():
    from src.j_utils import dated_url_for
    return dict(url_for=dated_url_for)


# ... rest of the imports and blueprints ...

if __name__ == '__main__':
    app.run(debug=config.debug, host=config.host, port=config.port)
```

---

### Step 3: Update individual modules to use config

#### 3.1 Update src/h_config.py

```python
"""
Configuration for Ramya - uses centralized config.
"""

import os
from src.config import get_config

config = get_config()

# API Keys
OPEN_ROUTER_API_KEY = config.api.openrouter_api_key
GOOGLE_CLIENT_ID = config.api.google_client_id
GOOGLE_CLIENT_SECRET = config.api.google_client_secret
REDIS_URL = config.api.redis_url

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_DB_PATH = config.paths.chromadb_path
AUDIO_DIR = os.path.join(BASE_DIR, config.paths.audio_dir)
LOG_DIR = os.path.join(BASE_DIR, config.paths.log_dir)

# Model Configuration
MODEL_RANKING = config.models.model_ranking

# Voice Configuration
ALLOWED_VOICES = [
    'en-US-JennyNeural',
    'en-US-GuyNeural',
    'en-GB-SoniaNeural',
    'en-GB-RyanNeural',
    'en-AU-NatashaNeural',
    'en-AU-WilliamNeural',
]

# Rate Limiting (from config)
RATE_LIMIT_CHAT = config.security.rate_limit_chat
RATE_LIMIT_CHAT_WINDOW = config.security.rate_limit_chat_window
RATE_LIMIT_TTS = config.security.rate_limit_tts
RATE_LIMIT_TTS_WINDOW = config.security.rate_limit_tts_window
RATE_LIMIT_STT = config.security.rate_limit_stt
RATE_LIMIT_STT_WINDOW = config.security.rate_limit_stt_window
```

---

### Step 4: Update .env.example

Create `.env.example`:

```bash
# =============================================================================
# Ramya: Your Digital Neighbour - Environment Variables
# =============================================================================
# Copy this file to .env and fill in your values

# =============================================================================
# Required
# =============================================================================

# Application Environment (development, staging, production)
APP_ENV=development

# API Keys
OPENROUTER_API_KEY=your-openrouter-api-key-here

# Secret Key (generate: python -c "import secrets; print(secrets.token_hex(32))")
SECRET_KEY=your-secret-key-at-least-32-characters

# =============================================================================
# Optional - Development
# =============================================================================

# Server
HOST=0.0.0.0
PORT=8080

# Paths
CHROMADB_PATH=ramya_memory_db
LOG_DIR=logs
LOG_FILE_NAME=ramya.log
AUDIO_DIR=static/audio

# CORS (comma-separated)
CORS_ALLOWED_ORIGINS=http://localhost:8080,http://127.0.0.1:8080

# Rate Limiting
RATE_LIMIT_CHAT=5
RATE_LIMIT_CHAT_WINDOW=60
RATE_LIMIT_TTS=10
RATE_LIMIT_TTS_WINDOW=60
RATE_LIMIT_STT=10
RATE_LIMIT_STT_WINDOW=60

# Redis
REDIS_URL=redis://localhost:6379/0

# Session
SESSION_LIFETIME=604800

# =============================================================================
# Optional - Production Only
# =============================================================================

# Google OAuth (optional)
# GOOGLE_CLIENT_ID=your-google-client-id
# GOOGLE_CLIENT_SECRET=your-google-client-secret

# Model
# DEFAULT_MODEL=meta-llama/llama-3.3-70b-instruct:free
```

---

### Step 5: Update security_config.py

Update `src/security_config.py` to use centralized config:

```python
"""
Security configuration for Ramya application.
Phase 2 & 4: Uses centralized config
"""

import os
from src.config import get_config


def get_security_headers():
    """Get security headers configuration based on environment."""
    config = get_config()
    is_production = config.env == 'Production'
    
    return {
        'force_https': is_production,
        'force_https_permanent': False,
        'strict_transport_security': 'max-age=31536000; includeSubDomains',
        'content_security_policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self' data:; connect-src 'self' https://openrouter.ai;",
        'x_frame_options': 'DENY',
        'x_xss_protection': '1; mode=block',
        'x_content_type_options': 'nosniff',
        'referrer_policy': 'strict-origin-when-cross-origin',
        'permissions_policy': 'geolocation=(), microphone=(), camera=()',
    }


def get_cors_config():
    """Get CORS configuration from config."""
    config = get_config()
    
    return {
        'origins': config.security.cors_allowed_origins,
        'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
        'allow_headers': ['Content-Type', 'Authorization', 'X-Requested-With'],
        'expose_headers': ['Content-Length', 'Content-Type'],
        'supports_credentials': True,
        'max_age': 3600,
    }


def get_rate_limit_config():
    """Get rate limiting configuration from config."""
    config = get_config()
    
    return {
        'chat': {
            'limit': config.security.rate_limit_chat,
            'window': config.security.rate_limit_chat_window,
        },
        'tts': {
            'limit': config.security.rate_limit_tts,
            'window': config.security.rate_limit_tts_window,
        },
        'stt': {
            'limit': config.security.rate_limit_stt,
            'window': config.security.rate_limit_stt_window,
        },
    }
```

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `src/config.py` | Create | Centralized configuration |
| `app.py` | Modify | Use centralized config |
| `src/h_config.py` | Modify | Use centralized config |
| `src/security_config.py` | Modify | Use centralized config |
| `.env.example` | Create | Example environment file |

---

## Verification Checklist

- [ ] Config loads from environment variables
- [ ] Different configs for dev/staging/production
- [ ] Startup validation works
- [ ] Missing required vars cause error in production
- [ ] Warnings displayed for non-critical issues

---

## Next Phase

After completing Phase 4, proceed to **Phase 5: Logging & Error Handling** to add:
- Structured JSON logging
- Request ID tracking
- Custom error handlers
