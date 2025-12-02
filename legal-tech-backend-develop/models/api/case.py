from datetime import datetime, date
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional

from models.pydantic import LegalSubject, ProbableCaseStats
from .information import LitigantInformation


class CaseDetailRequest(BaseModel):
    year: int = Field(..., description="Year of the case")
    role: int = Field(..., description="Role of the case")
    court_id: UUID = Field(..., description="Court ID")
    tribunal_id: UUID = Field(..., description="Tribunal ID")


class CourtInfo(BaseModel):
    id: UUID = Field(..., description="Court ID")
    recepthor_id: UUID = Field(..., description="External recepthor system ID")
    name: str = Field(..., description="Court name")
    code: int = Field(..., description="Court code")


class TribunalInfo(BaseModel):
    id: UUID = Field(..., description="Tribunal ID")
    recepthor_id: UUID = Field(..., description="External recepthor system ID")
    name: str = Field(..., description="Tribunal name")
    code: int = Field(..., description="Tribunal code")
    court_id: UUID | None = Field(None, description="Court ID")


class CaseDetailResponse(BaseModel):
    id: UUID = Field(..., description="Case detail ID")
    year: int = Field(..., description="Year of the case")
    role: int = Field(..., description="Role of the case")
    court_id: UUID = Field(..., description="Court ID")
    tribunal_id: UUID = Field(..., description="Tribunal ID")
    court: CourtInfo | None = Field(None, description="Court information")
    tribunal: TribunalInfo | None = Field(None, description="Tribunal information")


class CaseResponse(BaseModel):
    id: UUID = Field(..., description="Case ID")
    title: str = Field(..., description="Case title")
    city: str = Field(..., description="City where the case takes place")
    legal_subject: LegalSubject = Field(..., description="Legal subject of the case")
    winner: str | None = Field(..., description="Party that won the case")
    status: str = Field(..., description="Current status of the case")
    created_at: datetime = Field(..., description="Case creation time")
    simulated: bool = Field(False, description="Whether it is a simulated case or not")
    stats: ProbableCaseStats | None = Field(None, description="Probable case stats")
    details: CaseDetailResponse | None = Field(None, description="Case details")
    litigants: list[LitigantInformation] = Field([], description="Case litigants")
    case_recepthor_id: UUID | None = Field(None, description="External recepthor system case ID")


class ActionRequest(BaseModel):
    action_to_follow: str = Field(..., description="Action to follow")
    responsible: str = Field(..., description="Responsible person")
    deadline: date = Field(..., description="Deadline date")
    comment: Optional[str] = Field(None, description="Comment about the action")


class ActionResponse(BaseModel):
    id: UUID = Field(..., description="Action ID")
    case_id: UUID = Field(..., description="Case ID")
    action_to_follow: str = Field(..., description="Action to follow")
    responsible: str = Field(..., description="Responsible person")
    deadline: date = Field(..., description="Deadline date")
    completed: bool = Field(..., description="Whether the action is completed")
    comment: Optional[str] = Field(None, description="Comment about the action")


class ActionsResponse(BaseModel):
    actions: list[ActionResponse] = Field(..., description="List of actions")
    total_count: int = Field(..., description="Total number of actions")
