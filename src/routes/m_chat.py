from flask import request, jsonify, Response, Blueprint
from src.d_security_utils import sanitize_string, detect_injection
from src.f_auth import login_required
from src.j_utils import get_bot


chat_bp = Blueprint('chat', __name__)

# Try to use Redis-based rate limiter, fallback to in-memory
USE_REDIS_RATELIMIT = False
_rate_limiter_func = None

try:
    from src.rate_limiter import check_rate_limit
    _rate_limiter_func = check_rate_limit
    USE_REDIS_RATELIMIT = True
except ImportError:
    from src.d_security_utils import RateLimiter
    _rate_limiter_func = RateLimiter(limit=5, window=60)


def _check_rate_limit(limit_type: str, ip: str) -> tuple:
    """Check rate limit using appropriate limiter."""
    if USE_REDIS_RATELIMIT:
        return _rate_limiter_func(limit_type, ip)
    else:
        allowed = _rate_limiter_func.is_allowed(ip)
        return (allowed, 0 if not allowed else 1)


@chat_bp.route('/start_chat', methods=['POST'])
@login_required
def start_chat():
    """Start a new chat session."""
    bot = get_bot()
    data = request.json
    chat_name = sanitize_string(data.get("name", "default_chat"))
    safe_name = bot.start_new_chat(chat_name)  
    bot.summary = "No summary yet..."
    return jsonify({"status": "Chat started", "name": safe_name})


@chat_bp.route('/chats', methods=['GET'])
@login_required
def get_chats():
    """Get all chats for current user."""
    bot = get_bot()
    chats = bot.get_all_chats()
    return jsonify({"chats": chats})


@chat_bp.route('/delete_chat', methods=['POST'])
@login_required
def delete_chat():
    """Delete a chat session."""
    bot = get_bot()
    data = request.json
    chat_name = sanitize_string(data.get("name"))
    if bot.delete_chat(chat_name):
        return jsonify({"status": "Chat deleted"})
    return jsonify({"status": "Error deleting chat"}), 400


@chat_bp.route('/chat_history/<chat_name>', methods=['GET'])
@login_required
def get_history(chat_name):
    """Get chat history for a specific chat."""
    bot = get_bot()
    chat_name = sanitize_string(chat_name)
    history = bot.get_chat_history(chat_name)
    return jsonify({"history": history})


@chat_bp.route('/send_message', methods=['POST'])
@login_required
def send_message():
    """Send a message and get AI response."""
    ip = request.remote_addr or "unknown"
    
    is_allowed, _ = _check_rate_limit('chat', ip)
    if not is_allowed:
        return jsonify({
            "status": "error", 
            "message": "Whoa there! You're chatting too fast. Please wait a minute before sending more messages."
        }), 429

    user_data = request.json
    if not user_data or 'message' not in user_data:
        return jsonify({"status": "error", "message": "No message provided"}), 400
        
    user_message = sanitize_string(user_data.get("message"))
    if not user_message:
        return jsonify({"status": "error", "message": "Empty message"}), 400
        
    chat_name = sanitize_string(user_data.get("chat_name", ""))
    
    if detect_injection(user_message):
        return jsonify({
            "status": "error", 
            "message": "I'm sorry, I can't follow that instruction. Let's keep our conversation friendly and simple!"
        }), 400
    
    try:
        bot = get_bot()
        if chat_name:
            bot.start_new_chat(chat_name)
            
        def generate():
            for token in bot.get_response(user_message):
                yield token
        
        return Response(generate(), mimetype='text/plain')

    except Exception as e:
        return jsonify({"status": "error", "message": "Something went wrong in my brain."}), 500
