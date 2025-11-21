from pydantic import BaseModel, Field


class CaseStatsEventInformation(BaseModel):
    date: str | None = Field(None, description="Event creation date")
    type: str | None = Field(None, description="Event type")


class CaseStatsInformation(BaseModel):
    id: str = Field(..., description="Case stats ID")
    title: str = Field(..., description="Case title")
    legal_subject: str = Field(..., description="Case title")
    winner: str | None = Field(None, description="Winner legal party")
    status: str = Field("draft", description="Case status")
    created_at: str | None = Field(None, description="Case first event date")
    latest_step: str = Field("documents", description="Latest event type")
    court: str = Field(..., description="Case court")
    events: list[CaseStatsEventInformation] = Field([], description="Case relevant events")
    simulated: bool = Field(False, description="Whether the case is simulated or not")


class CaseStatsResponse(BaseModel):
    cases: list[CaseStatsInformation] = Field([], description="Cases information")
    case_count: int = Field(0, description="Total amount of cases after applying filters")
