from pydantic import BaseModel, Field


class DigitalCuratorsItem(BaseModel):
    folio: int | None = Field(None, description="Item folio")
    number: int | None = Field(None, description="Item number")
    year: int | None = Field(None, description="Item year")
    name: str | None = Field(None, description="Item owner")
    address: str | None = Field(None, description="Item address")
    event: str | None = Field(None, description="Item event")
