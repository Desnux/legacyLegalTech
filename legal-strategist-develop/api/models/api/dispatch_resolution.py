from pydantic import BaseModel, Field

from models.pydantic import (
    DispatchResolutionStructure,
)


class DispatchResolutionGenerationResponse(BaseModel):
    raw_text: str | None = Field(None, description="Raw text of a dispatch resolution related to a judicial collection")
    structured_output: DispatchResolutionStructure | None = Field(None, description="Structured output of a dispatch resolution related to a judicial collection")
