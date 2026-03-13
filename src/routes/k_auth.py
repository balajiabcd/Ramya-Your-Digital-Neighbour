"""
Authentication routes for Ramya.
Phase 3: Authentication System
"""

from flask import render_template, request, jsonify, url_for, redirect, session, Blueprint
from src.f_auth import login_required
import re


auth_bp = Blueprint('auth', __name__)


def validate_password(password: str):
    """Validate password strength."""
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    return True, None


def validate_username(username: str):
    """Validate username format."""
    if not username or len(username) < 3:
        return False, "Username must be at least 3 characters"
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    return True, None


def get_user_model():
    """Get user model instance."""
    from src.models.user_model import get_user_model as _get_model
    return _get_model()


@auth_bp.route('/register', methods=['POST'])
def register():
    """User registration API."""
    data = request.json or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')
    email = data.get('email', '').strip()
    
    is_valid, error = validate_username(username)
    if not is_valid:
        return jsonify({"status": "error", "message": error}), 400
    
    is_valid, error = validate_password(password)
    if not is_valid:
        return jsonify({"status": "error", "message": error}), 400
    
    user_model = get_user_model()
    result = user_model.create_user(username, password, email)
    
    if result['success']:
        return jsonify({
            "status": "success",
            "message": "Registration successful. Please login."
        }), 201
    else:
        return jsonify({
            "status": "error",
            "message": result.get('error', 'Registration failed')
        }), 400


@auth_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    """Login page - handles both GET and POST."""
    if 'user' in session:
        return redirect(url_for('home.home'))
    
    if request.method == 'POST':
        # Check if it's JSON (API) or Form
        if request.is_json:
            data = request.json or {}
            username = data.get('username', '').strip()
            password = data.get('password', '')
        else:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
        
        if not username or not password:
            if request.is_json:
                return jsonify({
                    "status": "error",
                    "message": "Username and password required"
                }), 400
            return render_template('login.html', error="Username and password required")
        
        user_model = get_user_model()
        
        if user_model.verify_user(username, password):
            session['user'] = {
                'username': username,
                'email': f"{username}@local.app",
                'name': username,
            }
            session.permanent = True
            
            if request.is_json:
                return jsonify({
                    "status": "success",
                    "message": "Login successful"
                })
            
            next_url = request.args.get('next')
            return redirect(next_url or url_for('home.home'))
        else:
            if request.is_json:
                return jsonify({
                    "status": "error",
                    "message": "Invalid username or password"
                }), 401
            return render_template('login.html', error="Invalid username or password")
            
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """Logout - clears session and redirects to login."""
    session.clear()
    return redirect(url_for('auth.login_page'))


@auth_bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    """Change user password."""
    data = request.json or {}
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    
    if not current_password or not new_password:
        return jsonify({
            "status": "error",
            "message": "Current and new password required"
        }), 400
    
    is_valid, error = validate_password(new_password)
    if not is_valid:
        return jsonify({"status": "error", "message": error}), 400
    
    username = session['user']['username']
    user_model = get_user_model()
    
    if not user_model.verify_user(username, current_password):
        return jsonify({
            "status": "error",
            "message": "Current password is incorrect"
        }), 401
    
    if user_model.update_password(username, new_password):
        return jsonify({
            "status": "success",
            "message": "Password updated successfully"
        })
    else:
        return jsonify({
            "status": "error",
            "message": "Failed to update password"
        }), 500


@auth_bp.route('/session', methods=['GET'])
def check_session():
    """Check if user is logged in."""
    if 'user' in session:
        return jsonify({
            "status": "authenticated",
            "user": session['user']
        })
    else:
        return jsonify({
            "status": "unauthenticated"
        }), 401
