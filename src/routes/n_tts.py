import re
import asyncio
import edge_tts
from flask import request, jsonify, Response, session, Blueprint
from src.f_auth import login_required
from src.h_config import ALLOWED_VOICES, AUDIO_DIR


tts_bp = Blueprint('tts', __name__)

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


@tts_bp.route('/tts_stream', methods=['POST'])
@login_required
def tts_stream():
    """Stream TTS audio for a single sentence."""
    ip = request.remote_addr or "unknown"
    
    is_allowed, _ = _check_rate_limit('tts', ip)
    if not is_allowed:
        return jsonify({"status": "error", "message": "Too many voice requests. Please slow down!"}), 429

    data = request.json
    if not data or 'text' not in data:
        return jsonify({"status": "error", "message": "No text provided"}), 400

    raw_text = data['text']
    clean_text = re.sub(r'[#*`_~>]', '', raw_text).strip()
    if not clean_text:
        return jsonify({"status": "error", "message": "Empty text"}), 400

    requested_voice = data.get('voice', 'en-US-JennyNeural')
    voice = requested_voice if requested_voice in ALLOWED_VOICES else 'en-US-JennyNeural'

    rate = data.get('rate', '+0%')
    if not re.match(r'^[+-]\d{1,3}%$', rate):
        rate = '+0%'

    pitch = data.get('pitch', '+0Hz')
    if not re.match(r'^[+-]\d{1,3}Hz$', pitch):
        pitch = '+0Hz'

    try:
        import tempfile
        import os
        
        temp_fd, temp_path = tempfile.mkstemp(suffix='.mp3')
        os.close(temp_fd)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            async def _generate():
                communicate = edge_tts.Communicate(clean_text, voice=voice, rate=rate, pitch=pitch)
                await communicate.save(temp_path)
            
            loop.run_until_complete(_generate())
        finally:
            loop.close()
        
        def stream_audio():
            try:
                with open(temp_path, 'rb') as f:
                    while chunk := f.read(8192):
                        yield chunk
            finally:
                try:
                    os.remove(temp_path)
                except:
                    pass
        
        return Response(stream_audio(), mimetype='audio/mpeg', headers={'Cache-Control': 'no-cache'})
    
    except Exception as e:
        print(f"TTS Stream error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": f"Voice streaming failed: {str(e)}"}), 500


@tts_bp.route('/tts', methods=['POST'])
@login_required
def tts():
    """Convert text to speech using Microsoft Edge TTS."""
    ip = request.remote_addr or "unknown"
    
    is_allowed, _ = _check_rate_limit('tts', ip)
    if not is_allowed:
        return jsonify({"status": "error", "message": "Too many voice requests. Please slow down!"}), 429

    data = request.json
    if not data or 'text' not in data:
        return jsonify({"status": "error", "message": "No text provided"}), 400

    raw_text = data['text']
    clean_text = re.sub(r'[#*`_~>]', '', raw_text).strip()
    if not clean_text:
        return jsonify({"status": "error", "message": "Empty text"}), 400

    requested_voice = data.get('voice', 'en-US-JennyNeural')
    voice = requested_voice if requested_voice in ALLOWED_VOICES else 'en-US-JennyNeural'

    rate = data.get('rate', '+0%')
    if not re.match(r'^[+-]\d{1,3}%$', rate):
        rate = '+0%'

    pitch = data.get('pitch', '+0Hz')
    if not re.match(r'^[+-]\d{1,3}Hz$', pitch):
        pitch = '+0Hz'

    audio_filename = f"reply_{session.get('user', {}).get('email', 'anon').split('@')[0]}.mp3"
    audio_path = AUDIO_DIR + "/" + audio_filename

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            async def _generate():
                communicate = edge_tts.Communicate(clean_text, voice=voice, rate=rate, pitch=pitch)
                await communicate.save(audio_path)
            
            loop.run_until_complete(_generate())
        finally:
            loop.close()
    except Exception as e:
        import traceback
        print(f"TTS Generation Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": f"Voice generation failed: {str(e)}"}), 500

    try:
        def stream_audio():
            with open(audio_path, 'rb') as f:
                while chunk := f.read(8192):
                    yield chunk
        
        return Response(stream_audio(), mimetype='audio/mpeg')
    except Exception as e:
        print(f"Audio streaming error: {e}")
        return jsonify({"status": "error", "message": "Audio streaming failed"}), 500
