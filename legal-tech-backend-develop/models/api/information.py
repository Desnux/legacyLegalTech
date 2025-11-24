from pydantic import BaseModel, Field


class LitigantInformation(BaseModel):
    id: str = Field(..., description="Litigant ID")
    name: str = Field(..., description="Litigant name")
    rut: str = Field(..., description="Litigant RUT")
    address: str | None = Field(None, description="Litigant address")
    role: str = Field(..., description="Litigant role")
    simulated: bool = Field(False, description="Whether the litigant is simulated or not")
    is_co_debtor: bool = Field(False, description="Whether the litigant is a co debtor or not")


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
    rol: int | None = Field(None, description="Case rol")
    year: int | None = Field(None, description="Case year")
    court: str = Field(..., description="Case court")
    tribunal: str = Field("to be assigned", description="Case tribunal")
    events: list[CaseStatsEventInformation] = Field([], description="Case relevant events")
    litigants: list[LitigantInformation] = Field([], description="Case litigants")
    simulated: bool = Field(False, description="Whether the case is simulated or not")
    amount: float | None = Field(None, description="Case amount")
    amount_currency: str | None = Field(None, description="Case amount currency")


class CaseStatsResponse(BaseModel):
    cases: list[CaseStatsInformation] = Field([], description="Cases information")
    case_count: int = Field(0, description="Total amount of cases after applying filters")
