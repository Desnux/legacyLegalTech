from pydantic import BaseModel, Field


class LawFirmCreate(BaseModel):
    """Request model for creating a Law Firm."""
    rut: str = Field(..., description="RUT de la firma de abogados")
    name: str = Field(..., description="Nombre de la firma de abogados")
    description: str | None = Field(None, description="Descripción de la firma de abogados")


class LawFirmResponse(BaseModel):
    """Response model for Law Firm data."""
    id: str = Field(..., description="Law Firm unique identifier")
    rut: str = Field(..., description="RUT de la firma de abogados")
    name: str = Field(..., description="Nombre de la firma de abogados")
    description: str | None = Field(None, description="Descripción de la firma de abogados")

    class Config:
        from_attributes = True

