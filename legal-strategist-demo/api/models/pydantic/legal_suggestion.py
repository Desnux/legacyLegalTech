from enum import Enum

from pydantic import BaseModel, Field


class SuggestionType(str, Enum):
    DEMAND_TEXT_CORRECTION = "demand_text_correction"
    EXCEPTIONS_RESPONSE = "exceptions_response"
    RESPONSE = "response"
    REQUEST = "request"
    COMPROMISE = "compromise"
    OTHER = "other"


class LegalSuggestion(BaseModel):
    name: str | None = Field(None, description="Suggestion name")
    description: str | None = Field(None, description="Short description of what the user should do")
    suggestion_type: SuggestionType | str | None = Field(None, description="Suggestion type")
    score: float | None = Field(None, description="How strongly the suggestion will benefit the user, from 0.0 (not at all) to 1.0 (they should do what is being suggested)")
