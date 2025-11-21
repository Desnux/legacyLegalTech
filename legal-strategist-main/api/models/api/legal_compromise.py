from pydantic import BaseModel, Field

from models.pydantic import (
    LegalCompromise,
)


class LegalCompromiseGenerationResponse(BaseModel):
    raw_text: str | None = Field(None, description="Raw text of a legal compromise related to a judicial collection")
    structured_output:  LegalCompromise | None = Field(None, description="Structured output of a legal compromise related to a judicial collection")
