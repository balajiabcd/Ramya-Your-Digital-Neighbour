"""
Tests for src/routes/k_auth.py (Auth Routes)
"""

import pytest
import json
import uuid


class TestAuthRoutes:
    """Test authentication routes."""
    
    def test_login_page_loads(self, client):
        """Test login page loads."""
        response = client.get('/login')
        assert response.status_code == 200
    
    def test_register_user_success(self, client):
        """Test user registration."""
        response = client.post('/register', 
            json={'username': 'testuser1', 'password': 'testpass123'},
            content_type='application/json')
        assert response.status_code in [201, 400]  # 400 if user exists
    
    def test_register_user_invalid_username(self, client):
        """Test registration with invalid username."""
        response = client.post('/register',
            json={'username': 'ab', 'password': 'testpass123'},
            content_type='application/json')
        assert response.status_code == 400
    
    def test_register_user_short_password(self, client):
        """Test registration with short password."""
        response = client.post('/register',
            json={'username': 'validuser', 'password': '123'},
            content_type='application/json')
        assert response.status_code == 400
    
    def test_session_endpoint_unauthenticated(self, client):
        """Test session check without auth."""
        response = client.get('/session')
        assert response.status_code == 401
    
    def test_session_endpoint_authenticated(self, authenticated_client):
        """Test session check with auth."""
        response = authenticated_client.get('/session')
        assert response.status_code == 200
    
    def test_logout_redirect(self, client):
        """Test logout redirects."""
        response = client.get('/logout', follow_redirects=False)
        assert response.status_code in [302, 200]

    def test_change_password_success(self, client):
        """Test successful password change."""
        # Generate unique username to avoid conflicts from previous test runs
        unique_username = f"chgpass_{uuid.uuid4().hex[:8]}"
        
        # 1. Register user
        reg_resp = client.post('/register', 
            json={'username': unique_username, 'password': 'oldpassword'},
            content_type='application/json')
        assert reg_resp.status_code == 201, f"Registration failed: {reg_resp.data}"
        
        # 2. Login
        log_resp = client.post('/login',
            json={'username': unique_username, 'password': 'oldpassword'},
            content_type='application/json')
        assert log_resp.status_code == 200, f"Login failed with 401: {log_resp.data}"
            
        # 3. Change password
        response = client.post('/change_password',
            json={'current_password': 'oldpassword', 'new_password': 'newtestpass123'},
            content_type='application/json')
        assert response.status_code == 200
        assert b"successfully" in response.data

    def test_change_password_invalid_current(self, client):
        """Test password change with wrong current password."""
        # Generate unique username to avoid conflicts from previous test runs
        unique_username = f"wrongpass_{uuid.uuid4().hex[:8]}"
        
        # 1. Register user
        reg_resp = client.post('/register', 
            json={'username': unique_username, 'password': 'correctpassword'},
            content_type='application/json')
        assert reg_resp.status_code == 201, f"Registration failed: {reg_resp.data}"
        
        # 2. Login
        log_resp = client.post('/login',
            json={'username': unique_username, 'password': 'correctpassword'},
            content_type='application/json')
        assert log_resp.status_code == 200, f"Login failed: {log_resp.data}"
            
        # 3. Change password with WRONG current
        response = client.post('/change_password',
            json={'current_password': 'WRONGpassword', 'new_password': 'newtestpass123'},
            content_type='application/json')
        assert response.status_code == 401
        assert b"Current password is incorrect" in response.data
