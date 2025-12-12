from fastapi import Request, HTTPException, Depends
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging

from database.ext_db import get_session, Session
from services.auth import UserAuthService, TokenService
from models.sql import User, UserRole


class OptimizedAuthMiddleware(BaseHTTPMiddleware):
    """
    Authentication middleware supporting JWT and static tokens.
    """

    def __init__(self, app):
        super().__init__(app)
        self.public_paths = (
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
            "/v1/extract/demand-text-input/",
            "/health",
            "/favicon.ico",
        )

    async def dispatch(self, request: Request, call_next):
        # Allow preflight
        if request.method == "OPTIONS":
            return await call_next(request)

        # Allow public routes
        if self._is_public_path(request.url.path):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JSONResponse(
                status_code=401,
                content={"detail": "Authorization header required"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth_header.replace("Bearer ", "").strip()
        session: Session | None = None

        try:
            session = next(get_session())
            user = await self._authenticate_user(token, session)

            request.state.user = user
            request.state.session = session

            return await call_next(request)

        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail},
                headers=e.headers,
            )
        except Exception as e:
            logging.exception("Auth middleware error")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"},
            )
        finally:
            if session:
                session.close()

    def _is_public_path(self, path: str) -> bool:
        PUBLIC_PREFIXES = (
            "/docs",
            "/redoc",
            "/openapi.json",
            "/v1/docs",
            "/v1/redoc",
            "/v1/openapi.json",
            "/v1/auth/login",
            "/v1/auth/register",
            "/v1/auth/validate-token",
            "/health",
            "/favicon.ico",
            "/generate/",
            "/generate/demand-exception/",
        )
        return any(path.startswith(p) for p in PUBLIC_PREFIXES)



    async def _authenticate_user(self, token: str, session: Session) -> User:
        # JWT auth
        try:
            user = UserAuthService.get_current_user(session, token)
            if user and user.active:
                return user
        except Exception as e:
            logging.debug(f"JWT auth failed: {e}")

        # Static token auth
        try:
            if TokenService.validate_token(token):
                return User(
                    id=None,
                    name="API_User",
                    hashed_password="",
                    role=UserRole.CLIENT,
                    active=True,
                )
        except Exception as e:
            logging.debug(f"Static token auth failed: {e}")

        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# -----------------------
# Dependencies
# -----------------------

def get_current_user(request: Request) -> User:
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


def get_current_user_optional(request: Request) -> User | None:
    return getattr(request.state, "user", None)


def get_current_session(request: Request) -> Session:
    session = getattr(request.state, "session", None)
    if not session:
        raise HTTPException(status_code=500, detail="Database session not available")
    return session


def require_role(required_role: str):
    def checker(request: Request):
        user = get_current_user(request)
        if user.role.value != required_role:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required role: {required_role}",
            )
        return user
    return checker


def require_admin(request: Request):
    return require_role("admin")(request)


def require_developer(request: Request):
    return require_role("developer")(request)
