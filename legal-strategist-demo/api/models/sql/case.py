from enum import Enum
from datetime import datetime
from typing import Any

from pydantic import model_validator
from sqlalchemy import Column, DateTime, Enum as SQLAlchemyEnum, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID, uuid4

from models.pydantic import LegalSubject
from .court import CourtCase
from .document import Document
from .litigant import Litigant
from .suggestion import CaseEventSuggestion


class CaseEventType(str, Enum):
    DEMAND_START = "demand_start"
    EXCEPTIONS = "exceptions"
    DISPATCH_RESOLUTION = "dispatch_resolution"
    RESOLUTION = "resolution"
    EXCEPTIONS_RESPONSE = "exceptions_response"
    REQUEST = "request"
    RESPONSE = "response"
    DEMAND_TEXT_CORRECTION = "demand_text_correction"
    COMPROMISE = "compromise"
    OTHER = "other"


class CaseParty(str, Enum):
    PLAINTIFFS = "plaintiffs"
    DEFENDANTS = "defendants"
    COURT = "court"
    EXTERNAL_PARTY = "external_party"


class CaseStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    FINISHED = "finished"


class CaseEvent(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    case_id: UUID = Field(
        ...,
        foreign_key="case.id",
        ondelete="CASCADE",
        nullable=False,
        description="Case ID",
    )
    case: "Case" = Relationship(
        back_populates="events",
        sa_relationship=ForeignKey("case.id"),
    )
    title: str = Field(..., description="Event title")
    content: dict[str, Any] | None = Field(
        sa_column=Column(JSON), 
        description="Event content as JSON",
    )
    type: CaseEventType = Field(
        default=CaseEventType.OTHER,
        sa_column=Column(SQLAlchemyEnum(CaseEventType), nullable=False),
        description="Case event type",
    )
    documents: list[Document] = Relationship(
        back_populates="case_event",
        sa_relationship=ForeignKey("document.id"),
    )
    source: CaseParty = Field(
        sa_column=Column(SQLAlchemyEnum(CaseParty), nullable=False),
        description="Party that initiated the event",
    )
    target: CaseParty = Field(
        sa_column=Column(SQLAlchemyEnum(CaseParty), nullable=False),
        description="Party that should respond to the event",
    )
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
        description="Case event creation time",
    )
    previous_event_id: UUID | None = Field(
        None,
        foreign_key="caseevent.id",
        nullable=True,
        description="Previous event ID",
    )
    next_event_id: UUID | None = Field(
        None,
        foreign_key="caseevent.id",
        nullable=True,
        description="Next event ID",
        ondelete="SET NULL",
    )
    previous_event: "CaseEvent" = Relationship(
        back_populates="next_event",
        sa_relationship=ForeignKey("caseevent.id"),
    )
    next_event: "CaseEvent" = Relationship(
        back_populates="previous_event",
        sa_relationship=ForeignKey("caseevent.id"),
    )
    simulated: bool = Field(False, description="Whether it is a simulated event or not")
    suggestions: list[CaseEventSuggestion] = Relationship(
        back_populates="case_event",
        sa_relationship=ForeignKey("caseeventsuggestion.id"),
    )

    @model_validator(mode="before")
    def validate_event_chain(cls, values):
        previous_event = values.get("previous_event")
        next_event = values.get("next_event")
        if previous_event and previous_event.next_event_id != values.get("id"):
            raise ValueError("Inconsistent previous_event linkage.")
        if next_event and next_event.previous_event_id != values.get("id"):
            raise ValueError("Inconsistent next_event linkage.")
        return values


class Case(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(..., description="Case title")
    city: str = Field(..., description="City where the case takes place")
    legal_subject: LegalSubject = Field(
        sa_column=Column(SQLAlchemyEnum(LegalSubject), nullable=False),
        description="Legal subject of the case",
    )
    winner: CaseParty | None = Field(
        sa_column=Column(SQLAlchemyEnum(CaseParty), nullable=True),
        description="Party that won the case",
    )
    status: CaseStatus = Field(CaseStatus.DRAFT, description="Current status of the case")
    events: list[CaseEvent] = Relationship(
        back_populates="case",
        sa_relationship=ForeignKey("caseevent.id"),
    )
    litigants: list[Litigant] = Relationship(
        back_populates="case",
        sa_relationship=ForeignKey("litigant.id"),
    )
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
        description="Case creation time",
    )
    court_cases: list[CourtCase] = Relationship(
        back_populates="case",
        sa_relationship=ForeignKey("courtcase.id"),
    )

    @model_validator(mode="before")
    def validate_winner(cls, values):
        status = values.get("status")
        winner = values.get("winner")
        if winner and status != CaseStatus.FINISHED:
            raise ValueError("Winner can only be set for finished cases.")
        return values
