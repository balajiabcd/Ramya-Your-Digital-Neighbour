from functools import wraps
from flask import session, jsonify, redirect, url_for, request


def login_required(f):
    """Decorator to require login for protected routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            print(f"DEBUG DECORATOR: 'user' not in session. Session keys: {list(session.keys())}")
            api_paths = ('/chat', '/start_chat', '/delete_chat', '/chats', '/tts', '/change_password')
            if any(request.path.startswith(p) for p in api_paths):
                return jsonify({"status": "error", "message": "Authentication required"}), 401
            return redirect(url_for('auth.login_page', next=request.url))
        return f(*args, **kwargs)
    return decorated_function
