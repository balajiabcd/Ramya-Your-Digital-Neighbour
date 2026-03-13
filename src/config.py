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
    session_lifetime: int = 3600 * 24 * 7
    
    rate_limit_chat: int = 5
    rate_limit_chat_window: int = 60
    rate_limit_tts: int = 10
    rate_limit_tts_window: int = 60
    rate_limit_stt: int = 10
    rate_limit_stt_window: int = 60
    
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
    max_content_length: int = 16 * 1024 * 1024
    
    security: SecurityConfig = field(default_factory=SecurityConfig)
    api: APIConfig = field(default_factory=APIConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    models: ModelConfig = field(default_factory=ModelConfig)
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Create config from environment variables."""
        env = os.getenv('APP_ENV', 'Development').lower()
        
        if env not in ['development', 'staging', 'production', 'testing']:
            raise ConfigError(f"Invalid APP_ENV: {env}. Must be development, staging, production, or testing")
        
        debug = env in ('development', 'testing')
        
        secret_key = os.getenv('SECRET_KEY', '')
        if env == 'production' and not secret_key:
            raise ConfigError("SECRET_KEY is required in production")
        if not secret_key:
            secret_key = "dev-secret-key-change-in-production"
        
        cors_origins = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
        cors_origins = [o.strip() for o in cors_origins if o.strip()]
        if not cors_origins:
            cors_origins = ["http://localhost:8080", "http://127.0.0.1:8080"]
        
        api_key = os.getenv('OPENROUTER_API_KEY', '')
        
        security = SecurityConfig(
            secret_key=secret_key,
            session_cookie_secure=env in ('production', 'staging'),
            session_cookie_httponly=True,
            session_cookie_samesite='Lax' if env in ('production', 'testing') else 'None',
            session_lifetime=int(os.getenv('SESSION_LIFETIME', str(3600 * 24 * 7))),
            rate_limit_chat=int(os.getenv('RATE_LIMIT_CHAT', '5')),
            rate_limit_chat_window=int(os.getenv('RATE_LIMIT_CHAT_WINDOW', '60')),
            rate_limit_tts=int(os.getenv('RATE_LIMIT_TTS', '10')),
            rate_limit_tts_window=int(os.getenv('RATE_LIMIT_TTS_WINDOW', '60')),
            rate_limit_stt=int(os.getenv('RATE_LIMIT_STT', '10')),
            rate_limit_stt_window=int(os.getenv('RATE_LIMIT_STT_WINDOW', '60')),
            cors_allowed_origins=cors_origins,
        )
        
        api = APIConfig(
            openrouter_api_key=api_key,
            google_client_id=os.getenv('GOOGLE_CLIENT_ID', ''),
            google_client_secret=os.getenv('GOOGLE_CLIENT_SECRET', ''),
            redis_url=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
        )
        
        paths = PathsConfig(
            chromadb_path=os.getenv('CHROMADB_PATH', 'ramya_memory_db'),
            log_dir=os.getenv('LOG_DIR', 'logs'),
            log_file_name=os.getenv('LOG_FILE_NAME', 'ramya.log'),
            audio_dir=os.getenv('AUDIO_DIR', 'static/audio'),
        )
        
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
        """Validate configuration."""
        warnings = []
        
        if self.env == 'Production':
            if len(self.security.secret_key) < 32:
                warnings.append("SECRET_KEY should be at least 32 characters in production")
            
            if self.security.cors_allowed_origins == ["http://localhost:8080"]:
                warnings.append("CORS_ALLOWED_ORIGINS not set for production")
        
        if not self.api.openrouter_api_key:
            warnings.append("OPENROUTER_API_KEY not set - AI features will not work")
        
        return warnings


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
    """Validate configuration on startup."""
    config = get_config()
    
    if config.env == 'Production':
        if not config.security.secret_key or config.security.secret_key == "dev-secret-key-change-in-production":
            raise ConfigError("SECRET_KEY must be changed in production")
        
        if not config.api.openrouter_api_key:
            raise ConfigError("OPENROUTER_API_KEY is required in production")
    
    warnings = config.validate()
    for warning in warnings:
        print(f"CONFIG WARNING: {warning}")
