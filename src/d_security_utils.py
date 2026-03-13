import re
import sys
import time
from collections import deque
from typing import Deque, Dict


def sanitize_string(text: str | None) -> str | None:
    """
    Strips HTML tags and leading/trailing whitespace from a string.
    """
    if not isinstance(text, str):
        return text
    
    clean_text = re.sub(r'<[^>]*>', '', text)
    return clean_text.strip()


class RateLimiter:
    """
    A simple sliding window rate limiter (in-memory).
    """
    def __init__(self, limit: int = 5, window: int = 60) -> None:
        self.limit = limit
        self.window = window
        self.requests: Dict[str, Deque[float]] = {}

    def is_allowed(self, ip: str) -> bool:
        now = time.time()
        if ip not in self.requests:
            self.requests[ip] = deque()
        
        window_start = now - self.window
        
        while self.requests[ip] and self.requests[ip][0] < window_start:
            self.requests[ip].popleft()
            
        if len(self.requests[ip]) < self.limit:
            self.requests[ip].append(now)
            return True
            
        return False


class RedisRateLimiter:
    """
    Redis-based rate limiter with in-memory fallback.
    """
    def __init__(self, limit: int = 5, window: int = 60) -> None:
        self.limit = limit
        self.window = window
        self._cache = None
        self._use_redis = False
        self._memory_requests: Dict[str, Deque[float]] = {}
    
    def _get_cache(self):
        if self._cache is None:
            try:
                from src.e_cache import get_cache
                self._cache = get_cache()
                self._use_redis = True
            except Exception:
                pass
        return self._cache
    
    def is_allowed(self, ip: str) -> bool:
        cache = self._get_cache()
        
        if cache and hasattr(cache, 'redis') and cache.redis:
            # Use Redis
            try:
                key = f"ratelimit:{ip}"
                count = cache.increment(key, self.window)
                return count <= self.limit
            except Exception:
                pass
        
        # Fallback to in-memory
        if not hasattr(self, '_memory_requests'):
            self._memory_requests: Dict[str, Deque[float]] = {}
        
        now = time.time()
        if ip not in self._memory_requests:
            self._memory_requests[ip] = deque()
        
        window_start = now - self.window
        
        while self._memory_requests[ip] and self._memory_requests[ip][0] < window_start:
            self._memory_requests[ip].popleft()
            
        if len(self._memory_requests[ip]) < self.limit:
            self._memory_requests[ip].append(now)
            return True
            
        return False


def validate_api_key(api_key: str | None) -> bool:
    """
    Validates the existence and format of the OpenRouter API key.
    Raises ValueError if the key is missing or invalid.
    """
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is missing!")

    if not isinstance(api_key, str) or not api_key.startswith("sk-or-v1-"):
        raise ValueError("Invalid OPENROUTER_API_KEY format! Key must start with 'sk-or-v1-'.")

    if len(api_key) < 30:
        raise ValueError("OPENROUTER_API_KEY is too short! The key seems truncated or invalid.")

    print("API Key format validated. Heartbeat detected.")
    return True


def detect_injection(text: str) -> bool:
    """
    Detects common prompt injection patterns to protect the AI's persona.
    """
    if not isinstance(text, str):
        return False
        
    patterns = [
        r"ignore (all )?previous instructions",
        r"system prompt",
        r"your (secret )?instructions",
        r"forget (everything )?i said",
        r"new (role|persona)",
        r"(SELECT|INSERT|UPDATE|DELETE|DROP|UNION) ",
        r"--",
        r"/\*.*?\*/"
    ]
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False
