from typing import Any, TYPE_CHECKING

from sqlalchemy import Column, Enum as SQLAlchemyEnum, ForeignKey, JSON
from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID, uuid4

from models.pydantic import SuggestionType


if TYPE_CHECKING:
    from .case import CaseEvent


class CaseEventSuggestion(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    case_event_id: UUID = Field(
        ...,
        foreign_key="caseevent.id",
        ondelete="CASCADE",
        nullable=False,
        description="CaseEvent ID",
    )
    case_event: "CaseEvent" = Relationship(
        back_populates="suggestions",
        sa_relationship=ForeignKey("caseevent.id"),
    )
    name: str = Field(..., description="Suggestion name")
    content: dict[str, Any] | None = Field(
        sa_column=Column(JSON), 
        description="Event suggestion as JSON",
    )
    type: SuggestionType = Field(
        default=SuggestionType.OTHER,
        sa_column=Column(SQLAlchemyEnum(SuggestionType), nullable=False),
        description="Case event type",
    )
    storage_key: str | None = Field(None, description="Unique key to access the stored file")
    score: float = Field(0.0, description="Suggestion relative strength")
