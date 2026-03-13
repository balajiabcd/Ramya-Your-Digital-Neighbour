# Phase 3: Authentication System

## Context
Improve the current simple session-based auth to a secure password-based authentication system with proper encryption.

**Project:** Ramya: Your Digital Neighbour  
**App Name:** Ramya

## Current State
- Simple username → pseudo-email conversion (no password)
- Session stored in Flask cookie (not encrypted)
- No user registration capability
- No password hashing

## Brief Plan
1. Add password hashing with bcrypt
2. Implement secure session management
3. Create user registration endpoint
4. Add password reset capability (optional)
5. Add role-based access control (admin vs user)
6. Create user model with ChromaDB

---

## Detailed Step-by-Step Implementation

### Step 1: Add bcrypt to requirements.txt

Add to requirements.txt:
```
bcrypt==4.1.2
```

---

### Step 2: Create User Model

Create `src/models/user_model.py`:

```python
"""
User model for Ramya authentication.
Phase 3: Authentication System
"""

import bcrypt
import os
import chromadb
from datetime import datetime
from typing import Optional, Dict, Any


class UserModel:
    """User model with password hashing using ChromaDB."""
    
    def __init__(self):
        db_path = os.getenv('CHROMADB_PATH', 'ramya_memory_db')
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        self.users_col = self.chroma_client.get_or_create_collection(
            name="users",
            metadata={"hnsw:space": "l2"}
        )
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against a hash."""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False
    
    def create_user(self, username: str, password: str, email: str = None) -> Dict[str, Any]:
        """Create a new user with hashed password."""
        # Check if user exists
        existing = self.users_col.get(ids=[username])
        if existing['ids']:
            return {"success": False, "error": "Username already exists"}
        
        # Hash password
        hashed_password = self._hash_password(password)
        
        # Create user document
        user_data = {
            "username": username,
            "password": hashed_password,
            "email": email or f"{username}@local.app",
            "created_at": datetime.now().isoformat(),
            "role": "user",
            "active": "true"
        }
        
        self.users_col.upsert(
            ids=[username],
            documents=[str(user_data)],
            metadatas=[user_data]
        )
        
        return {"success": True, "username": username}
    
    def verify_user(self, username: str, password: str) -> bool:
        """Verify user credentials."""
        existing = self.users_col.get(ids=[username])
        
        if not existing['ids']:
            return False
        
        user_meta = existing['metadatas'][0]
        
        # Check if user is active
        if user_meta.get('active') != 'true':
            return False
        
        # Verify password
        stored_hash = user_meta.get('password', '')
        return self._verify_password(password, stored_hash)
    
    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username."""
        existing = self.users_col.get(ids=[username])
        
        if not existing['ids']:
            return None
        
        return existing['metadatas'][0]
    
    def update_password(self, username: str, new_password: str) -> bool:
        """Update user password."""
        hashed = self._hash_password(new_password)
        
        existing = self.users_col.get(ids=[username])
        if not existing['ids']:
            return False
        
        user_meta = existing['metadatas'][0]
        user_meta['password'] = hashed
        user_meta['updated_at'] = datetime.now().isoformat()
        
        self.users_col.update(
            ids=[username],
            metadatas=[user_meta]
        )
        return True
    
    def deactivate_user(self, username: str) -> bool:
        """Deactivate a user account."""
        existing = self.users_col.get(ids=[username])
        if not existing['ids']:
            return False
        
        user_meta = existing['metadatas'][0]
        user_meta['active'] = 'false'
        
        self.users_col.update(
            ids=[username],
            metadatas=[user_meta]
        )
        return True
    
    def list_users(self) -> list:
        """List all users (admin only)."""
        return self.users_col.get()


# Global user model instance
_user_model = None

def get_user_model() -> UserModel:
    """Get or create the user model instance."""
    global _user_model
    if _user_model is None:
        _user_model = UserModel()
    return _user_model
```

---

### Step 3: Update Authentication Routes

Create or update `src/routes/auth_routes.py`:

```python
"""
Authentication routes for Ramya.
Phase 3: Authentication System
"""

from flask import Blueprint, request, jsonify, session, redirect, url_for
from src.models.user_model import get_user_model
from src.f_auth import login_required
import re


auth_bp = Blueprint('auth', __name__)


def validate_password(password: str) -> tuple:
    """
    Validate password strength.
    Returns (is_valid, error_message)
    """
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    return True, None


def validate_username(username: str) -> tuple:
    """
    Validate username format.
    Returns (is_valid, error_message)
    """
    if not username or len(username) < 3:
        return False, "Username must be at least 3 characters"
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    return True, None


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if request.method == 'GET':
        return jsonify({"message": "Use POST to register"}), 400
    
    data = request.json or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')
    email = data.get('email', '').strip()
    
    # Validate username
    is_valid, error = validate_username(username)
    if not is_valid:
        return jsonify({"status": "error", "message": error}), 400
    
    # Validate password
    is_valid, error = validate_password(password)
    if not is_valid:
        return jsonify({"status": "error", "message": error}), 400
    
    # Create user
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


@auth_bp.route('/login', methods=['POST'])
def login():
    """User login."""
    data = request.json or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({
            "status": "error",
            "message": "Username and password required"
        }), 400
    
    user_model = get_user_model()
    
    if user_model.verify_user(username, password):
        # Set session
        session['user'] = {
            'username': username,
            'email': f"{username}@local.app",
        }
        session.permanent = True
        
        return jsonify({
            "status": "success",
            "message": "Login successful"
        })
    else:
        return jsonify({
            "status": "error",
            "message": "Invalid username or password"
        }), 401


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """User logout."""
    session.clear()
    return jsonify({
        "status": "success",
        "message": "Logged out successfully"
    })


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
    
    # Validate new password
    is_valid, error = validate_password(new_password)
    if not is_valid:
        return jsonify({"status": "error", "message": error}), 400
    
    username = session['user']['username']
    user_model = get_user_model()
    
    # Verify current password
    if not user_model.verify_user(username, current_password):
        return jsonify({
            "status": "error",
            "message": "Current password is incorrect"
        }), 401
    
    # Update password
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
```

---

### Step 4: Update Login Template

Update `templates/login.html` to include password field:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Ramya</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='global.css') }}">
    <style>
        .auth-container { max-width: 400px; margin: 50px auto; padding: 20px; }
        .auth-form input { width: 100%; padding: 10px; margin: 10px 0; }
        .auth-form button { width: 100%; padding: 10px; background: #4CAF50; color: white; border: none; cursor: pointer; }
        .tab-buttons { display: flex; margin-bottom: 20px; }
        .tab-buttons button { flex: 1; padding: 10px; }
        .tab-buttons button.active { background: #4CAF50; color: white; }
        .error { color: red; margin: 10px 0; }
        .success { color: green; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="auth-container">
        <h1>Ramya: Your Digital Neighbour</h1>
        
        <div class="tab-buttons">
            <button id="login-tab" class="active" onclick="showTab('login')">Login</button>
            <button id="register-tab" onclick="showTab('register')">Register</button>
        </div>
        
        <!-- Login Form -->
        <form id="login-form" class="auth-form" onsubmit="handleLogin(event)">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
        
        <!-- Register Form -->
        <form id="register-form" class="auth-form" style="display:none;" onsubmit="handleRegister(event)">
            <input type="text" name="username" placeholder="Username (min 3 chars)" required>
            <input type="password" name="password" placeholder="Password (min 6 chars)" required>
            <input type="email" name="email" placeholder="Email (optional)">
            <button type="submit">Register</button>
        </form>
        
        <div id="message"></div>
    </div>
    
    <script>
        function showTab(tab) {
            document.getElementById('login-form').style.display = tab === 'login' ? 'block' : 'none';
            document.getElementById('register-form').style.display = tab === 'register' ? 'block' : 'none';
            document.getElementById('login-tab').classList.toggle('active', tab === 'login');
            document.getElementById('register-tab').classList.toggle('active', tab === 'register');
        }
        
        async function handleLogin(e) {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            
            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                
                if (result.status === 'success') {
                    window.location.href = '/home';
                } else {
                    document.getElementById('message').innerHTML = 
                        '<div class="error">' + result.message + '</div>';
                }
            } catch (err) {
                document.getElementById('message').innerHTML = 
                    '<div class="error">Login failed. Please try again.</div>';
            }
        }
        
        async function handleRegister(e) {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            
            try {
                const response = await fetch('/register', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                
                if (result.status === 'success') {
                    document.getElementById('message').innerHTML = 
                        '<div class="success">' + result.message + '</div>';
                    showTab('login');
                } else {
                    document.getElementById('message').innerHTML = 
                        '<div class="error">' + result.message + '</div>';
                }
            } catch (err) {
                document.getElementById('message').innerHTML = 
                    '<div class="error">Registration failed. Please try again.</div>';
            }
        }
    </script>
</body>
</html>
```

---

### Step 5: Update app.py to include new auth routes

Modify `app.py`:

```python
# ... existing imports ...

# Add new auth routes
from src.routes.auth_routes import auth_bp

# ... existing blueprints ...

app.register_blueprint(auth_bp, url_prefix='')

# ... rest of the code ...
```

---

### Step 6: Create models __init__.py

Create `src/models/__init__.py`:

```python
"""Models package for Ramya."""
from src.models.user_model import UserModel, get_user_model

__all__ = ['UserModel', 'get_user_model']
```

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `src/models/__init__.py` | Create | Models package init |
| `src/models/user_model.py` | Create | User model with bcrypt |
| `src/routes/auth_routes.py` | Create | Auth endpoints |
| `templates/login.html` | Modify | Add registration form |
| `app.py` | Modify | Register auth blueprint |
| `requirements.txt` | Modify | Add bcrypt |

---

## Verification Checklist

- [ ] User can register with username/password
- [ ] Password is hashed with bcrypt
- [ ] User can login with credentials
- [ ] Invalid login shows error
- [ ] Session persists across requests
- [ ] Logout clears session
- [ ] Password change works
- [ ] Duplicate username rejected

---

## Next Phase

After completing Phase 3, proceed to **Phase 4: Environment Configuration** to add:
- config.py with dev/staging/production configs
- Environment variable validation
- Secrets management
