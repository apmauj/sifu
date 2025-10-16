"""
Authentication Routes for SIFU
Login, logout, and user management endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from auth_models import LoginRequest, TokenResponse, User
from auth_service import auth_service
from auth_middleware import get_current_user, require_admin
from typing import List

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest):
    """Authenticate user and return access token"""
    user = auth_service.authenticate_user(login_data.username, login_data.password)

    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    # Create access token
    access_token = auth_service.create_access_token(
        data={"sub": user.username, "role": user.role.value}
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=auth_service.access_token_expire_minutes * 60,
        user=user,
    )


@router.post("/logout")
async def logout():
    """Logout endpoint (client-side token removal)"""
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user


@router.get("/users", response_model=List[User])
async def get_users(current_user: User = Depends(require_admin)):
    """Get all users (admin only)"""
    # In production, this should query the database
    users_db = auth_service._get_demo_users()

    users = []
    for username, user_data in users_db.items():
        user = User(
            id=user_data["id"],
            username=username,
            email=user_data["email"],
            role=user_data["role"],
            permissions=auth_service._get_role_permissions(user_data["role"]),
            is_active=user_data["is_active"],
            created_at=user_data["created_at"],
        )
        users.append(user)

    return users


@router.get("/permissions")
async def get_permissions(current_user: User = Depends(get_current_user)):
    """Get current user permissions"""
    return {
        "user": current_user.username,
        "role": current_user.role.value,
        "permissions": [p.value for p in current_user.permissions],
    }
