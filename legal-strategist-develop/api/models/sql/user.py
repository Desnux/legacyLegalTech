from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from passlib.hash import bcrypt
from sqlalchemy import Column, DateTime, Enum as SQLAlchemyEnum, ForeignKey
from sqlalchemy.sql import func
from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID, uuid4


if TYPE_CHECKING:
    from .litigant import Litigant


class UserGroup(str, Enum):
    EXECUTIVE_CASE = "executive_case"
    IN_HOUSE_SUITE = "in_house_suite"


class UserRole(str, Enum):
    ADMIN = "admin"
    DEVELOPER = "developer"
    TESTER = "tester"
    CLIENT = "client"
    BOT = "bot"
    GUEST = "guest"


class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(..., description="User name")
    hashed_password: str = Field(..., description="Hashed user password")
    role: UserRole = Field(
        default=UserRole.GUEST,
        sa_column=Column(SQLAlchemyEnum(UserRole), nullable=False),
        description="User role",
    )
    active: bool = Field(True, description="Whether the user can use the application or not")
    litigants: list["Litigant"] = Relationship(
        back_populates="user",
        sa_relationship=ForeignKey("litigant.id"),
    )
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
        description="User creation time",
    )

    def set_password(self, password: str) -> None:
        self.hashed_password = bcrypt.hash(password)

    def verify_password(self, password: str) -> bool:
        return bcrypt.verify(password, self.hashed_password)
