from pydantic import BaseModel, Field

from models.pydantic import DigitalCuratorsItem


class DigitalCuratorsRequest(BaseModel):
    name: str = Field(..., description="Query name")


class DigitalCuratorsResponse(BaseModel):
    message: str = Field(..., description="Digital curators response")
    status: int = Field(..., description="HTTP status code")
    data: list[DigitalCuratorsItem] = Field([], description="Extracted information")
    total_items: int = Field(..., description="Total items")
