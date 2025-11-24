from datetime import datetime
from pydantic import BaseModel
from uuid import UUID
from typing import Optional

from models.sql import UserRole


class LawFirmBasic(BaseModel):
    """Basic Law Firm information for nested responses."""
    id: UUID
    rut: str
    name: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: UUID
    username: str
    role: UserRole
    expires_at: datetime


class UserResponse(BaseModel):
    id: UUID
    name: str
    role: UserRole
    active: bool
    created_at: datetime
    law_firm: Optional[LawFirmBasic] = None

class CreateUserResponse(BaseModel):
    id: UUID
    name: str
    role: UserRole
    active: bool
    created_at: datetime
    law_firm_id: Optional[UUID] = None

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class UpdateUserRoleRequest(BaseModel):
    role: UserRole 