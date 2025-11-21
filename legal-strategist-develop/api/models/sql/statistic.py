from datetime import date

from sqlalchemy import ForeignKey
from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID, uuid4


class CaseStatsEvent(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)    
    case_stats: "CaseStats" = Relationship(
        back_populates="events",
        sa_relationship=ForeignKey("casestats.id"),
    )
    case_stats_id: UUID = Field(
        ...,
        foreign_key="casestats.id",
        ondelete="CASCADE",
        nullable=False,
        description="Case ID",
    )
    creation_date: date | None = Field(None, description="Event creation date")
    name: str = Field(..., description="Event name")
    type: str | None = Field(None, description="Event type")
    enumeration: str | None = Field(None, description="Event enumeration")
    page_index: int | None = Field(None, description="Event page index inside case ebook")


class CaseStats(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    bank: str = Field(..., description="Bank name")
    court_number: int | None = Field(None, description="Court number")
    court_city: str = Field(..., description="Court city")
    case_role: str = Field(..., description="Case role")
    year: int = Field(..., description="Case year")
    case_type: str = Field(..., description="Case type")
    legal_stage: str = Field(..., description="Current legal stage")
    title: str = Field(..., description="Case title")
    amount: float | None = Field(None, description="Amount to pay")
    currency: str | None = Field(None, description="Amount currency")
    result: str | None = Field(None, description="Case result")
    duration: int | None = Field(None, description="Case duration in days")
    events: list[CaseStatsEvent] = Relationship(
        back_populates="case_stats",
        sa_relationship=ForeignKey("casestatsevent.id"),
    )
