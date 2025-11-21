from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID

from models.pydantic import LegalSubject, ProbableCaseStats


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
