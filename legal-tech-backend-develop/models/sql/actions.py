
from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID, uuid4
from datetime import date
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .case import Case

class Action(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    case_id: UUID = Field(
        ...,
        foreign_key="case.id",
        ondelete="CASCADE",
        nullable=False,
        description="Case ID",
    )
    case: "Case" = Relationship(back_populates="actions")
    action_to_follow: str = Field(..., description="Action to follow")
    responsible: str = Field(..., description="Responsible person")
    deadline: date = Field(..., description="Deadline date")
    completed: bool = Field(default=False, description="Whether the action is completed")
    comment: Optional[str] = Field(default=None, description="Comment about the action")
