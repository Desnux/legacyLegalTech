from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from .case_detail import CaseDetail
    from .court import Court


class Tribunal(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    recepthor_id: UUID = Field(..., description="External recepthor system ID for integration")
    name: str = Field(..., description="Tribunal name")
    code: int = Field(..., description="Tribunal code")
    court_id: UUID | None = Field(
        None,
        foreign_key="court.id",
        description="Court ID"
    )
    court: "Court" = Relationship(back_populates="tribunals")
    case_details: list["CaseDetail"] = Relationship(back_populates="tribunal")
