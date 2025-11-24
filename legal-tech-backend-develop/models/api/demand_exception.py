from pydantic import BaseModel, Field

from models.pydantic import (
    DemandExceptionStructure,
)


class DemandExceptionGenerationResponse(BaseModel):
    raw_text: str | None = Field(None, description="Raw text of a demand exception related to a judicial collection")
    structured_output:  DemandExceptionStructure | None = Field(None, description="Structured output of a demand exception related to a judicial collection")
