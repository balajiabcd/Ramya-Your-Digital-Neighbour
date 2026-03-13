from flask import request, jsonify, Blueprint
from src.f_auth import login_required
from src.b_stt_engine import get_stt_engine


stt_bp = Blueprint('stt', __name__)

# Try to use Redis-based rate limiter, fallback to in-memory
USE_REDIS_RATELIMIT = False
_rate_limiter_func = None

try:
    from src.rate_limiter import check_rate_limit
    _rate_limiter_func = check_rate_limit
    USE_REDIS_RATELIMIT = True
except ImportError:
    from src.d_security_utils import RateLimiter
    _rate_limiter_func = RateLimiter(limit=10, window=60)


def _check_rate_limit(limit_type: str, ip: str) -> tuple:
    """Check rate limit using appropriate limiter."""
    if USE_REDIS_RATELIMIT:
        return _rate_limiter_func(limit_type, ip)
    else:
        allowed = _rate_limiter_func.is_allowed(ip)
        return (allowed, 0 if not allowed else 1)


@stt_bp.route('/stt', methods=['POST'])
@login_required
def speech_to_text():
    """Convert speech to text using Whisper."""
    ip = request.remote_addr or "unknown"
    
    is_allowed, _ = _check_rate_limit('stt', ip)
    if not is_allowed:
        return jsonify({"error": "Too many requests. Please slow down!"}), 429

    if 'audio' not in request.files:
        return jsonify({"error": "No audio provided"}), 400
    
    audio_file = request.files['audio']
    audio_bytes = audio_file.read()
    
    if len(audio_bytes) < 1000:
        return jsonify({"error": "Audio too short"}), 400
    
    try:
        stt_engine = get_stt_engine()
        text = stt_engine.transcribe(audio_bytes)
        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"error": "Transcription failed"}), 500
