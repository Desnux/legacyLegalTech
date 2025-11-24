from datetime import datetime, timedelta
from fastapi import Body, Depends, HTTPException
from uuid import UUID

from database.ext_db import get_session, Session
from models.api import error_response
from models.api.auth import (
    CreateUserResponse,
    LoginRequest, 
    LoginResponse, 
    UserResponse, 
    ChangePasswordRequest,
    UpdateUserRoleRequest,
    LawFirmBasic
)
from models.api.user import UserCreate
from models.sql import User, UserRole, LawFirm
from services.auth import UserAuthService
from .middleware import get_current_active_user, require_admin
from . import router
from sqlmodel import select
from sqlalchemy.orm import selectinload

@router.post("/login/", response_model=LoginResponse)
async def login(
    login_data: LoginRequest = Body(...),
    session: Session = Depends(get_session)
):
    """Login with username and password."""
    try:
        user = UserAuthService.authenticate_user(
            session, 
            login_data.username, 
            login_data.password
        )
        
        if not user:
            return error_response("Invalid username or password", 401)
        
        access_token_expires = timedelta(minutes=UserAuthService.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = UserAuthService.create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires
        )
        
        expires_at = datetime.utcnow() + access_token_expires
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user.id,
            username=user.name,
            role=user.role,
            expires_at=expires_at
        )
        
    except Exception as e:
        return error_response(f"Login failed: {str(e)}", 500)


@router.post("/register/", response_model=CreateUserResponse)
async def register(
    user_data: UserCreate = Body(...),
    session: Session = Depends(get_session)
):
    """Register a new user."""
    try:
        user = UserAuthService.create_user(session, user_data)
        
        return CreateUserResponse(
            id=user.id,
            name=user.name,
            role=user.role,
            active=user.active,
            created_at=user.created_at,
            law_firm_id=user.law_firm_id
        )
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Registration failed: {str(e)}", 500)


@router.get("/me/", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get current user information."""
    try:
        # Reload user with law_firm relationship
        statement = select(User).where(User.id == current_user.id).options(selectinload(User.law_firm))
        user = session.exec(statement).first()
        
        if not user:
            return error_response("User not found", 404)
        
        return UserResponse(
            id=user.id,
            name=user.name,
            role=user.role,
            active=user.active,
            created_at=user.created_at,
            law_firm=LawFirmBasic.model_validate(user.law_firm) if user.law_firm else None
        )
    except Exception as e:
        return error_response(f"Failed to get user info: {str(e)}", 500)


@router.post("/change-password/")
async def change_password(
    password_data: ChangePasswordRequest = Body(...),
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Change user password."""
    try:
        # Verify current password
        if not current_user.verify_password(password_data.current_password):
            return error_response("Current password is incorrect", 400)
        
        # Update password
        current_user.set_password(password_data.new_password)
        session.add(current_user)
        session.commit()
        
        return {"message": "Password changed successfully"}
        
    except Exception as e:
        return error_response(f"Password change failed: {str(e)}", 500)


# Admin endpoints
@router.get("/users/", response_model=list[UserResponse])
async def get_all_users(
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """Get all users (admin only)."""
    try:
        from sqlmodel import select
        from sqlalchemy.orm import selectinload
        
        # Query with eager loading of law_firm relationship
        statement = select(User).options(selectinload(User.law_firm))
        users = session.exec(statement).all()
        
        return [
            UserResponse(
                id=user.id,
                name=user.name,
                role=user.role,
                active=user.active,
                created_at=user.created_at,
                law_firm=LawFirmBasic.model_validate(user.law_firm) if user.law_firm else None
            )
            for user in users
        ]
        
    except Exception as e:
        return error_response(f"Failed to get users: {str(e)}", 500)


@router.get("/users/{user_id}/", response_model=UserResponse)
async def get_user_by_id(
    user_id: UUID,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """Get user by ID (admin only)."""
    try:
        from sqlmodel import select
        from sqlalchemy.orm import selectinload
        
        # Query with eager loading of law_firm relationship
        statement = select(User).where(User.id == user_id).options(selectinload(User.law_firm))
        user = session.exec(statement).first()
        
        if not user:
            return error_response("User not found", 404)
        
        return UserResponse(
            id=user.id,
            name=user.name,
            role=user.role,
            active=user.active,
            created_at=user.created_at,
            law_firm=LawFirmBasic.model_validate(user.law_firm) if user.law_firm else None
        )
        
    except Exception as e:
        return error_response(f"Failed to get user: {str(e)}", 500)


@router.put("/users/{user_id}/role/", response_model=UserResponse)
async def update_user_role(
    user_id: UUID,
    role_data: UpdateUserRoleRequest = Body(...),
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """Update user role (admin only)."""
    try:
        from sqlmodel import select
        from sqlalchemy.orm import selectinload
        
        user = UserAuthService.update_user_role(session, user_id, role_data.role)
        
        if not user:
            return error_response("User not found", 404)
        
        # Reload user with law_firm relationship
        statement = select(User).where(User.id == user_id).options(selectinload(User.law_firm))
        user = session.exec(statement).first()
        
        return UserResponse(
            id=user.id,
            name=user.name,
            role=user.role,
            active=user.active,
            created_at=user.created_at,
            law_firm=LawFirmBasic.model_validate(user.law_firm) if user.law_firm else None
        )
        
    except Exception as e:
        return error_response(f"Failed to update user role: {str(e)}", 500)


@router.delete("/users/{user_id}/")
async def deactivate_user(
    user_id: UUID,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """Deactivate user (admin only)."""
    try:
        if current_user.id == user_id:
            return error_response("Cannot deactivate yourself", 400)
        
        success = UserAuthService.deactivate_user(session, user_id)
        
        if not success:
            return error_response("User not found", 404)
        
        return {"message": "User deactivated successfully"}
        
    except Exception as e:
        return error_response(f"Failed to deactivate user: {str(e)}", 500) 