"""
Authentication Service for SIFU
Handles user authentication, token generation and validation
"""

import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from auth_models import User, UserRole, Permission, LoginRequest, TokenResponse, get_role_permissions
import secrets

class AuthService:
    """Authentication service"""

    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET_KEY", secrets.token_hex(32))
        self.algorithm = "HS256"
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    def hash_password(self, password: str) -> str:
        """Hash a password"""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        # For demo purposes, create default users
        # In production, this should query a database
        users_db = self._get_demo_users()

        user_data = users_db.get(username)
        if not user_data:
            return None

        if not self.verify_password(password, user_data["hashed_password"]):
            return None

        # Create User object
        user = User(
            id=user_data["id"],
            username=username,
            email=user_data["email"],
            role=user_data["role"],
            permissions=get_role_permissions(user_data["role"]),
            is_active=user_data["is_active"],
            created_at=user_data["created_at"]
        )

        return user

    def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from JWT token"""
        payload = self.decode_token(token)
        if not payload:
            return None

        username = payload.get("sub")
        if not username:
            return None

        # In production, fetch user from database
        users_db = self._get_demo_users()
        user_data = users_db.get(username)

        if not user_data:
            return None

        return User(
            id=user_data["id"],
            username=username,
            email=user_data["email"],
            role=user_data["role"],
            permissions=get_role_permissions(user_data["role"]),
            is_active=user_data["is_active"],
            created_at=user_data["created_at"]
        )

    def _get_demo_users(self) -> Dict[str, Dict[str, Any]]:
        """Get demo users for development"""
        # Default admin user
        admin_password = self.hash_password("admin123")

        return {
            "admin": {
                "id": "admin-001",
                "username": "admin",
                "email": "admin@sifu.local",
                "hashed_password": admin_password,
                "role": UserRole.ADMIN,
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            "manager": {
                "id": "manager-001",
                "username": "manager",
                "email": "manager@sifu.local",
                "hashed_password": self.hash_password("manager123"),
                "role": UserRole.MANAGER,
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            "user": {
                "id": "user-001",
                "username": "user",
                "email": "user@sifu.local",
                "hashed_password": self.hash_password("user123"),
                "role": UserRole.USER,
                "is_active": True,
                "created_at": datetime.utcnow()
            }
        }

# Global auth service instance
auth_service = AuthService()
