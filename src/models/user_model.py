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
        existing = self.users_col.get(ids=[username])
        if existing['ids']:
            return {"success": False, "error": "Username already exists"}
        
        hashed_password = self._hash_password(password)
        
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
        
        if user_meta.get('active') != 'true':
            return False
        
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


_user_model = None

def get_user_model() -> UserModel:
    """Get or create the user model instance."""
    global _user_model
    if _user_model is None:
        _user_model = UserModel()
    return _user_model
