from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field



class ContactDetail(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    contactDetail: Optional[str] = None
    recommended: Optional[bool] = None


class Person(BaseModel):
    name: Optional[str] = None
    rut: Optional[str] = None


class Shareholder(Person):
    participation: Optional[float] = None


class OwnedProperty(BaseModel):
    address: Optional[str] = None
    rol: Optional[str] = None
    comuna: Optional[str] = None
    comunaCode: Optional[str] = None


class OwnedSociety(BaseModel):
    societyName: Optional[str] = None
    rut: Optional[str] = None
    participation: Optional[float] = None


class OwnerDataResponse(BaseModel):
    ownerName: Optional[str] = None
    ownerRut: Optional[str] = None
    ownerType: Optional[str] = None
    ownerTelephones: List[ContactDetail] = Field(default_factory=list)
    ownerEmails: List[ContactDetail] = Field(default_factory=list)
    ownerRepresentatives: List[Person] = Field(default_factory=list)
    ownerShareholders: List[Shareholder] = Field(default_factory=list)
    ownedProperties: List[OwnedProperty] = Field(default_factory=list)
    ownedSocieties: List[OwnedSociety] = Field(default_factory=list)

# Updated: Made all fields optional to handle API variations