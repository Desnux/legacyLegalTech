from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, Enum as SQLAlchemyEnum, ForeignKey
from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID, uuid4

from .user import User


if TYPE_CHECKING:
    from .case import Case
    from .document import Document


class LitigantRole(str, Enum):
    PLAINTIFF = "plaintiff"
    DEFENDANT = "defendant"
    COURT = "court"
    SPONSORING_ATTORNEY = "sponsoring_attorney"
    DEFENDANT_ATTORNEY = "defendant_attorney"
    LEGAL_REPRESENTATIVE = "legal_representative"
    EXTERNAL_PARTY = "external_party"


class Litigant(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(..., description="Litigant name")
    rut: str = Field(..., description="Litigant RUT")
    address: str | None = Field(None, description="Litigant address", nullable=True)
    case_id: UUID = Field(
        ...,
        foreign_key="case.id",
        ondelete="CASCADE",
        nullable=False,
        description="Case ID",
    )
    case: "Case" = Relationship(
        back_populates="litigants",
    )
    role: LitigantRole = Field(
        sa_column=Column(SQLAlchemyEnum(LitigantRole), nullable=False),
        description="Litigant role",
    )
    user_id: UUID | None = Field(
        None,
        foreign_key="user.id",
        nullable=True,
        description="User ID",
    )
    user: User = Relationship(
        back_populates="litigants",
    )
    documents: list["Document"] = Relationship(
        back_populates="author",
    )
    represented_litigant_id: UUID | None = Field(
        None,
        foreign_key="litigant.id",
        nullable=True, 
        description="Litigant being represented",
    )
    represented_litigant: "Litigant" = Relationship(
        back_populates="legal_representatives",
        sa_relationship_kwargs={"remote_side": "Litigant.id"}
    )
    legal_representatives: list["Litigant"] = Relationship(
        back_populates="represented_litigant", 
    )
    simulated: bool = Field(False, description="Whether the litigant is simulated or not")
    is_co_debtor: bool = Field(False, description="Whether the litigant is a co debtor or not")
