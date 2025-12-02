from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator
from uuid import UUID

from models.sql import UserRole


class UserCreate(BaseModel):
    name: str
    password: str
    role: UserRole = UserRole.GUEST
    law_firm_id: Optional[UUID] = None

    @field_validator("name")
    def validate_name(cls, value):
        if len(value) < 3:
            raise ValueError("Name must be at least 3 characters long.")
        return value
    
    @field_validator("password")
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        return value


class UserRead(BaseModel):
    id: UUID
    name: str
    role: UserRole
    created_at: datetime
    last_interaction_at: datetime
    active: bool
