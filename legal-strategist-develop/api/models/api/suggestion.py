import json
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class SuggestionRequest(BaseModel):
    id: UUID = Field(..., description="Suggestion ID")
    password: str = Field(..., description="PJUD Password")
    rut: str = Field(..., description="PJUD RUT")

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class SuggestionResponse(BaseModel):
    message: str = Field(..., description="PJUD Response")
    status: int = Field(..., description="HTTP status code")
