from pydantic import BaseModel, Field
from uuid import UUID


class TribunalWithCourtInfo(BaseModel):
    """Tribunal information with court details for receptor."""
    id: UUID = Field(..., description="Tribunal ID")
    recepthor_id: UUID = Field(..., description="External recepthor system ID")
    name: str = Field(..., description="Tribunal name")
    code: int = Field(..., description="Tribunal code")
    court_id: UUID | None = Field(None, description="Court ID")
    court_name: str | None = Field(None, description="Court name")
    court_code: int | None = Field(None, description="Court code")


class ReceptorDetailResponse(BaseModel):
    """Response model for receptor detail with tribunal information."""
    id: UUID = Field(..., description="Receptor detail ID")
    tribunal: TribunalWithCourtInfo | None = Field(None, description="Tribunal information with court details")


class ReceptorResponse(BaseModel):
    """Response model for receptor with details."""
    id: UUID = Field(..., description="Receptor ID")
    recepthor_external_id: UUID = Field(..., description="External receptor ID")
    name: str | None = Field(None, description="Receptor name")
    primary_email: str | None = Field(None, description="Primary email address")
    secondary_email: str | None = Field(None, description="Secondary email address")
    primary_phone: str | None = Field(None, description="Primary phone number")
    secondary_phone: str | None = Field(None, description="Secondary phone number")
    address: str | None = Field(None, description="Physical address")
    details: list[ReceptorDetailResponse] = Field([], description="Receptor details with tribunal associations")

