from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, RootModel


class ContactDetail(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    contactDetail: Optional[str] = None
    recommended: Optional[bool] = None


class Contactability(BaseModel):
    telephones: List[ContactDetail] = Field(default_factory=list)
    emails: List[ContactDetail] = Field(default_factory=list)


class OwnerData(BaseModel):
    ownerName: Optional[str] = None
    ownerRut: Optional[str] = None
    ownerType: Optional[str] = None
    contactability: Optional[Contactability] = None


class SIIData(BaseModel):
    rol: Optional[str] = None
    block: Optional[int] = None
    blockCode: Optional[int] = None
    address: Optional[str] = None
    comuna: Optional[str] = None
    comunaCode: Optional[str] = None
    region: Optional[str] = None
    useType: Optional[str] = None
    fiscalValue: Optional[int] = None
    contributionFee: Optional[int] = None
    utilSurface: Optional[int] = None
    totalSurface: Optional[int] = None
    condominium: Optional[bool] = None


class Construction(BaseModel):
    constructionMaterial: Optional[str] = None
    constructionQuality: Optional[str] = None
    constructionYear: Optional[int] = None
    constructionSurface: Optional[int] = None
    materialUnit: Optional[str] = None


class TaxDue(BaseModel):
    period: Optional[str] = None
    amount: Optional[int] = None
    dueDate: Optional[str] = None
    status: Optional[str] = None


class TaxesData(BaseModel):
    taxDues: List[TaxDue] = Field(default_factory=list)


class PropertyHistoryItem(BaseModel):
    address: Optional[str] = None
    comunaCode: Optional[str] = None
    comuna: Optional[str] = None
    rol: Optional[str] = None
    date: Optional[str] = None
    price: Optional[float] = None
    surfaceUtil: Optional[int] = None
    surfaceTotal: Optional[int] = None
    destinoCode: Optional[str] = None
    transactionFojas: Optional[str] = None
    transactionNumber: Optional[str] = None
    transactionYear: Optional[str] = None
    pricePerSquareMeter: Optional[float] = None


class SimilarSale(BaseModel):
    address: Optional[str] = None
    comunaCode: Optional[str] = None
    comuna: Optional[str] = None
    rol: Optional[str] = None
    date: Optional[str] = None
    price: Optional[float] = None
    surfaceUtil: Optional[int] = None
    surfaceTotal: Optional[int] = None
    pricePerSquareMeter: Optional[float] = None
    destinoCode: Optional[str] = None
    transactionFojas: Optional[str] = None
    transactionNumber: Optional[str] = None
    transactionYear: Optional[str] = None
    distance: Optional[float] = None
    propertyType: Optional[str] = None


class MarketEvolutionItem(BaseModel):
    period: Optional[str] = None
    count: Optional[int] = None
    average: Optional[float] = None


class MarketData(BaseModel):
    propertyHistory: List[PropertyHistoryItem] = Field(default_factory=list)
    similarSales: List[SimilarSale] = Field(default_factory=list)
    marketEvolution: List[MarketEvolutionItem] = Field(default_factory=list)


class GoogleData(BaseModel):
    streetViewImage: Optional[str] = None
    mapViewImage: Optional[str] = None
    additionalStreetViewImages: List[str] = Field(default_factory=list)


class Address(BaseModel):
    name: Optional[str] = None
    house_number: Optional[str] = None
    road: Optional[str] = None
    neighbourhood: Optional[str] = None
    suburb: Optional[str] = None
    city: Optional[str] = None
    county: Optional[str] = None
    state: Optional[str] = None
    postcode: Optional[str] = None
    country: Optional[str] = None
    country_code: Optional[str] = None


class Place(BaseModel):
    lat: Optional[str] = None
    lon: Optional[str] = None
    place_class: Optional[str] = Field(default=None, alias="class")
    type: Optional[str] = None
    name: Optional[str] = None
    address: Optional[Address] = None
    walkingTime: Optional[int] = None
    walkingDistance: Optional[float] = None

    model_config = dict(populate_by_name=True)

class NearbyPlacesData(BaseModel):
    education: List[Place] = Field(default_factory=list)
    commerce: List[Place] = Field(default_factory=list)
    health: List[Place] = Field(default_factory=list)
    restaurants: List[Place] = Field(default_factory=list)


class PRCData(BaseModel):
    region: Optional[str] = None
    comunas: Optional[str] = None
    zones: Optional[str] = None
    zoneNames: Optional[str] = None
    description: Optional[str] = None
    permittedUses: Optional[str] = None
    prohibitedUses: Optional[str] = None
    layers: Optional[str] = None
    observations: Optional[str] = None
    documents: Optional[str] = None


class PropertyDataResponse(BaseModel):
    ownerData: List[OwnerData] = Field(default_factory=list)
    siiData: Optional[SIIData] = None
    constructions: List[Construction] = Field(default_factory=list)
    taxesData: Optional[TaxesData] = None
    marketData: Optional[MarketData] = None
    googleData: Optional[GoogleData] = None
    nearbyPlacesData: Optional[NearbyPlacesData] = None
    prcData: Optional[PRCData] = None 