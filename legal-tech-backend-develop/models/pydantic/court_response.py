from pydantic import BaseModel, Field


class CourtResponse(BaseModel):
    """Response model for Court data."""
    id: str = Field(..., description="Court unique identifier")
    recepthor_id: str = Field(..., description="External recepthor system ID for integration")
    name: str = Field(..., description="Court name")
    code: int = Field(..., description="Court code")

    class Config:
        from_attributes = True
