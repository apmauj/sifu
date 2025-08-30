#!/usr/bin/env python3
"""
Script de configuración de RBAC (Role-Based Access Control) para SIFU
Implementa autenticación básica y control de acceso basado en roles
"""

import os
import secrets
from pathlib import Path
from datetime import datetime

def create_auth_models():
    """Crea modelos de autenticación y autorización"""
    auth_models = '''"""
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
        Permission.USER_CREATE, Permission.USER_READ, Permission.USER_UPDATE, Permission.USER_DELETE,
        Permission.EXCHANGE_READ, Permission.EXCHANGE_UPDATE, Permission.EXCHANGE_DELETE,
        Permission.REPORT_READ, Permission.REPORT_GENERATE,
        Permission.SYSTEM_HEALTH, Permission.SYSTEM_CONFIG
    ],
    UserRole.MANAGER: [
        Permission.USER_READ,
        Permission.EXCHANGE_READ, Permission.EXCHANGE_UPDATE,
        Permission.REPORT_READ, Permission.REPORT_GENERATE,
        Permission.SYSTEM_HEALTH
    ],
    UserRole.USER: [
        Permission.EXCHANGE_READ,
        Permission.REPORT_READ,
        Permission.SYSTEM_HEALTH
    ],
    UserRole.GUEST: [
        Permission.SYSTEM_HEALTH
    ]
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
'''

    try:
        with open("auth_models.py", "w", encoding="utf-8") as f:
            f.write(auth_models)
        print("✅ Modelos de autenticación creados: auth_models.py")
        return True
    except Exception as e:
        print(f"❌ Error creando modelos de autenticación: {e}")
        return False

def create_auth_service():
    """Crea servicio de autenticación"""
    auth_service = '''"""
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
'''

    try:
        with open("auth_service.py", "w", encoding="utf-8") as f:
            f.write(auth_service)
        print("✅ Servicio de autenticación creado: auth_service.py")
        return True
    except Exception as e:
        print(f"❌ Error creando servicio de autenticación: {e}")
        return False

def create_auth_middleware():
    """Crea middleware de autenticación y autorización"""
    auth_middleware = '''"""
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
'''

    try:
        with open("auth_middleware.py", "w", encoding="utf-8") as f:
            f.write(auth_middleware)
        print("✅ Middleware de autenticación creado: auth_middleware.py")
        return True
    except Exception as e:
        print(f"❌ Error creando middleware de autenticación: {e}")
        return False

def create_auth_routes():
    """Crea rutas de autenticación"""
    auth_routes = '''"""
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
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )

    # Create access token
    access_token = auth_service.create_access_token(
        data={"sub": user.username, "role": user.role.value}
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=auth_service.access_token_expire_minutes * 60,
        user=user
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
async def get_users(
    current_user: User = Depends(require_admin)
):
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
            created_at=user_data["created_at"]
        )
        users.append(user)

    return users

@router.get("/permissions")
async def get_permissions(current_user: User = Depends(get_current_user)):
    """Get current user permissions"""
    return {
        "user": current_user.username,
        "role": current_user.role.value,
        "permissions": [p.value for p in current_user.permissions]
    }
'''

    try:
        with open("auth_routes.py", "w", encoding="utf-8") as f:
            f.write(auth_routes)
        print("✅ Rutas de autenticación creadas: auth_routes.py")
        return True
    except Exception as e:
        print(f"❌ Error creando rutas de autenticación: {e}")
        return False

def update_main_for_auth():
    """Actualiza main.py para incluir autenticación"""
    try:
        with open("main.py", "r", encoding="utf-8") as f:
            content = f.read()

        # Verificar si ya tiene los imports de auth
        if "from auth_routes import" not in content:
            # Agregar imports después del último import existente
            import_lines = []
            in_imports = False
            last_import_index = -1

            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith('from ') or line.strip().startswith('import '):
                    in_imports = True
                    last_import_index = i
                elif in_imports and line.strip() and not line.strip().startswith('#'):
                    break

            if last_import_index >= 0:
                # Insertar imports después del último import
                lines.insert(last_import_index + 1, "")
                lines.insert(last_import_index + 2, "# Authentication and Authorization")
                lines.insert(last_import_index + 3, "from auth_routes import router as auth_router")

                # Buscar donde se incluyen los routers
                router_include_index = -1
                for i, line in enumerate(lines):
                    if 'app.include_router' in line:
                        router_include_index = i
                        break

                if router_include_index >= 0:
                    # Agregar router de auth después del último include_router
                    last_router_index = router_include_index
                    for i in range(router_include_index + 1, len(lines)):
                        if 'app.include_router' in lines[i]:
                            last_router_index = i

                    lines.insert(last_router_index + 1, "")
                    lines.insert(last_router_index + 2, "# Authentication routes")
                    lines.insert(last_router_index + 3, "app.include_router(auth_router)")

                    new_content = '\n'.join(lines)

                    with open("main.py", "w", encoding="utf-8") as f:
                        f.write(new_content)

                    print("✅ main.py actualizado con rutas de autenticación")
                    return True

        print("⚠️  main.py ya tiene rutas de autenticación configuradas")
        return True

    except Exception as e:
        print(f"❌ Error actualizando main.py: {e}")
        return False

def create_env_auth_vars():
    """Crea variables de entorno para autenticación"""
    env_content = '''
# Authentication Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Default Users (for development only)
# admin:admin123
# manager:manager123
# user:user123
'''

    try:
        # Verificar si .env ya existe
        if os.path.exists(".env"):
            with open(".env", "r", encoding="utf-8") as f:
                existing_content = f.read()

            if "JWT_SECRET_KEY" not in existing_content:
                with open(".env", "a", encoding="utf-8") as f:
                    f.write("\n" + env_content)
                print("✅ Variables de autenticación agregadas a .env")
            else:
                print("⚠️  Variables de autenticación ya existen en .env")
        else:
            with open(".env", "w", encoding="utf-8") as f:
                f.write(env_content)
            print("✅ Archivo .env creado con variables de autenticación")

        return True

    except Exception as e:
        print(f"❌ Error configurando variables de entorno: {e}")
        return False

def main():
    """Función principal de configuración RBAC"""
    print("🔐 Configuración RBAC (Role-Based Access Control) para SIFU")
    print("=" * 60)

    # Crear modelos de autenticación
    if not create_auth_models():
        return 1

    # Crear servicio de autenticación
    if not create_auth_service():
        return 1

    # Crear middleware de autenticación
    if not create_auth_middleware():
        return 1

    # Crear rutas de autenticación
    if not create_auth_routes():
        return 1

    # Actualizar main.py
    if not update_main_for_auth():
        return 1

    # Configurar variables de entorno
    if not create_env_auth_vars():
        return 1

    print("\n" + "=" * 60)
    print("✅ Configuración RBAC completada exitosamente")
    print("\n📋 Próximos pasos:")
    print("   1. Reiniciar contenedores: docker-compose down && docker-compose up -d")
    print("   2. Probar login: POST https://localhost/auth/login")
    print("   3. Verificar permisos: GET https://localhost/auth/permissions")
    print("   4. Para producción: Configurar base de datos de usuarios")

    print("\n🔐 Características implementadas:")
    print("   ✅ Autenticación JWT con roles")
    print("   ✅ Control de acceso basado en permisos")
    print("   ✅ Middleware de autorización")
    print("   ✅ Endpoints de login/logout")
    print("   ✅ Usuarios demo para desarrollo")

    print("\n👥 Usuarios de prueba:")
    print("   Admin: admin / admin123")
    print("   Manager: manager / manager123")
    print("   User: user / user123")

    return 0

if __name__ == "__main__":
    exit(main())
