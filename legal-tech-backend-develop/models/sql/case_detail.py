
from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from .case import Case
    from .court import Court
    from .tribunal import Tribunal


class CaseDetail(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    case_id: UUID = Field(
        ...,
        foreign_key="case.id",
        ondelete="CASCADE",
        nullable=False,
        description="Case ID",
    )
    case: "Case" = Relationship(back_populates="details")
    year: int = Field(..., description="Year of the case")
    role: int = Field(..., description="Role of the case")
    court_id: UUID = Field(
        ...,
        foreign_key="court.id",
        ondelete="CASCADE",
        nullable=False,
        description="Court ID",
    )
    court: "Court" = Relationship(back_populates="case_details")
    tribunal_id: UUID = Field(
        ...,
        foreign_key="tribunal.id",
        ondelete="CASCADE",
        nullable=False,
        description="Tribunal ID",
    )
    tribunal: "Tribunal" = Relationship(back_populates="case_details")