"""
Authentication and Authorization Middleware for FastAPI
"""

from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
from typing import Optional, List
from auth_models import User, Permission
from auth_service import auth_service

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Dependency to get current authenticated user"""
    token = credentials.credentials

    user = auth_service.get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user

def require_permissions(required_permissions: List[Permission]):
    """Dependency factory for permission checking"""

    async def permission_checker(user: User = Depends(get_current_user)) -> User:
        """Check if user has required permissions"""
        from auth_models import has_any_permission

        if not has_any_permission(user, required_permissions):
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )

        return user

    return permission_checker

def require_role(required_role: str):
    """Dependency factory for role checking"""

    async def role_checker(user: User = Depends(get_current_user)) -> User:
        """Check if user has required role"""
        if user.role.value != required_role:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required"
            )

        return user

    return role_checker

# Convenience dependencies for common use cases
require_admin = require_role("admin")
require_manager = require_role("manager")
require_user = require_role("user")

# Permission-based dependencies
require_user_management = require_permissions([
    Permission.USER_READ,
    Permission.USER_UPDATE,
    Permission.USER_DELETE
])

require_exchange_management = require_permissions([
    Permission.EXCHANGE_READ,
    Permission.EXCHANGE_UPDATE
])

require_report_access = require_permissions([
    Permission.REPORT_READ,
    Permission.REPORT_GENERATE
])
