from fastapi import Request, HTTPException, Depends
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging

from config import Config
from database.ext_db import get_session, Session
from services.auth import UserAuthService, TokenService
from models.sql import User, UserRole


class OptimizedAuthMiddleware(BaseHTTPMiddleware):
    """
    Optimized Middleware that applies authentication automatically.
    Supports both JWT and static tokens with efficient session management.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.public_paths = [
            "/docs",
            "/redoc", 
            "/openapi.json",
            "/v1/docs",
            "/v1/redoc",
            "/v1/openapi.json",
            "/v1/auth/login/",
            "/v1/auth/register/",
            "/v1/auth/validate-token/",
            "/v1/homespotter/",
            "/health",
            "/favicon.ico",
            "/v1/extract/demand-text-input/",
        ]
    
    async def dispatch(self, request: Request, call_next):
        try:
            if request.method == "OPTIONS":
                return await call_next(request)
            if self._is_public_path(request.url.path):
                return await call_next(request)
            
            auth_header = request.headers.get("Authorization")
            if not auth_header: 
                raise HTTPException(
                    status_code=401,
                    detail="Authorization header required",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            token = auth_header.replace("Bearer ", "")
            
            # Create session and authenticate user
            session = next(get_session())
            try:
                user = await self._authenticate_user(token, session)
                request.state.user = user
                request.state.session = session
                
                response = await call_next(request)
                return response
            finally:
                # Close session after the request is complete
                session.close()
            
        except HTTPException as e:
            raise
        except Exception as e:
            logging.error(f"Middleware error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error"
            )
    
    def _is_public_path(self, path: str) -> bool:
        """Check if the path is public."""
        for public_path in self.public_paths:
            if path.startswith(public_path):
                return True
        return False
    
    async def _authenticate_user(self, token: str, session: Session) -> User:
        """Authenticate user using JWT or static token with provided session."""
        try:
            # Try JWT authentication first
            try:
                user = UserAuthService.get_current_user(session, token)
                if user:
                    logging.info(f"JWT auth: {user.name}")
                    return user
            except Exception as e:
                logging.debug(f"JWT auth failed: {e}")
            
            # Try static token authentication
            try:
                if TokenService.validate_token(token):
                    temp_user = User(
                        id=None,
                        name="API_User",
                        hashed_password="",
                        role=UserRole.CLIENT,
                        active=True
                    )
                    logging.info("Static token auth successful")
                    return temp_user
            except Exception as e:
                logging.debug(f"Static token auth failed: {e}")
            
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"Auth error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Authentication service error"
            )


# Dependency functions for endpoints
def get_current_user(request: Request) -> User:
    """
    Get the current user from the request state.
    Useful for endpoints that want to access the authenticated user.
    """
    user = getattr(request.state, 'user', None)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


def get_current_user_optional(request: Request) -> User | None:
    """
    Get the current user from the request state (optional).
    Returns None if no user is authenticated.
    """
    return getattr(request.state, 'user', None)


def get_current_session(request: Request) -> Session:
    """
    Get the current database session from the request state.
    Useful for endpoints that need database access.
    """
    session = getattr(request.state, 'session', None)
    if not session:
        raise HTTPException(status_code=500, detail="Database session not available")
    return session


# Role-based access control dependencies
def require_role(required_role: str):
    """
    Dependency factory for role-based access control.
    Usage: @router.get("/admin-only/", dependencies=[Depends(require_role("admin"))])
    """
    def role_checker(request: Request):
        user = get_current_user(request)
        if user.role.value != required_role:
            raise HTTPException(
                status_code=403, 
                detail=f"Access denied. Required role: {required_role}"
            )
        return user
    return role_checker


def require_admin(request: Request):
    """Require admin role for access."""
    return require_role("admin")(request)


def require_developer(request: Request):
    """Require developer role for access."""
    return require_role("developer")(request)
