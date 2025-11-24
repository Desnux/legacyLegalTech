from __future__ import annotations

from pydantic import BaseModel, Field


class OwnedPropertyDetailed(BaseModel):
    """Minimal representation of an owned property including registration details.

    This structure is returned by HomeSpotter when requesting all properties that
    belong to a given RUT.
    """

    address: str = Field(..., description="Full address of the property")
    rol: str = Field(..., description="Unique SII rol identifier (block-lot)")
    comuna: str = Field(..., description="Name of the comuna (municipality)")
    comunaCode: str = Field(..., description="Numeric comuna code")
    foja: str = Field(..., description="Foja (page) of the property registration")
    number: str = Field(..., description="Registration number")
    year: str = Field(..., description="Year of the registration") 