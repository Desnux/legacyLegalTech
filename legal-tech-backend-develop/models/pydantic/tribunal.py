from pydantic import BaseModel, Field
from uuid import UUID


class TribunalResponse(BaseModel):
    """Response model for Tribunal data."""
    id: str = Field(..., description="Tribunal unique identifier")
    recepthor_id: str = Field(..., description="External recepthor system ID for integration")
    name: str = Field(..., description="Tribunal name")
    code: int = Field(..., description="Tribunal code")
    court_id: str | None = Field(None, description="Court ID associated with this tribunal")

    class Config:
        from_attributes = True
