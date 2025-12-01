"""
Authentication and Authorization Models for SIFU
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime


class UserRole(str, Enum):
    """User roles in the system"""

    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    GUEST = "guest"


class Permission(str, Enum):
    """System permissions"""

    # User management
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"

    # Exchange rates
    EXCHANGE_READ = "exchange:read"
    EXCHANGE_UPDATE = "exchange:update"
    EXCHANGE_DELETE = "exchange:delete"

    # Reports
    REPORT_READ = "report:read"
    REPORT_GENERATE = "report:generate"

    # System
    SYSTEM_HEALTH = "system:health"
    SYSTEM_CONFIG = "system:config"


class User(BaseModel):
    """User model"""

    id: str
    username: str
    email: str
    role: UserRole
    permissions: List[Permission] = []
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None


class LoginRequest(BaseModel):
    """Login request model"""

    username: str
    password: str


class TokenResponse(BaseModel):
    """Token response model"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: User


class AuthError(BaseModel):
    """Authentication error model"""

    error: str
    message: str
    details: Optional[str] = None


# Role-based permission mappings
ROLE_PERMISSIONS = {
    UserRole.ADMIN: [
        Permission.USER_CREATE,
        Permission.USER_READ,
        Permission.USER_UPDATE,
        Permission.USER_DELETE,
        Permission.EXCHANGE_READ,
        Permission.EXCHANGE_UPDATE,
        Permission.EXCHANGE_DELETE,
        Permission.REPORT_READ,
        Permission.REPORT_GENERATE,
        Permission.SYSTEM_HEALTH,
        Permission.SYSTEM_CONFIG,
    ],
    UserRole.MANAGER: [
        Permission.USER_READ,
        Permission.EXCHANGE_READ,
        Permission.EXCHANGE_UPDATE,
        Permission.REPORT_READ,
        Permission.REPORT_GENERATE,
        Permission.SYSTEM_HEALTH,
    ],
    UserRole.USER: [
        Permission.EXCHANGE_READ,
        Permission.REPORT_READ,
        Permission.SYSTEM_HEALTH,
    ],
    UserRole.GUEST: [Permission.SYSTEM_HEALTH],
}


def get_role_permissions(role: UserRole) -> List[Permission]:
    """Get permissions for a specific role"""
    return ROLE_PERMISSIONS.get(role, [])


def has_permission(user: User, permission: Permission) -> bool:
    """Check if user has a specific permission"""
    return permission in user.permissions


def has_any_permission(user: User, permissions: List[Permission]) -> bool:
    """Check if user has any of the specified permissions"""
    return any(perm in user.permissions for perm in permissions)
