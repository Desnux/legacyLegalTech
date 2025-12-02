from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class IssuerCompanyData(BaseModel):
    issuerCompanyLogo: Optional[str] = None
    issuerCompanyName: Optional[str] = None


# ------------------------------------------------------------------
# Actives (assets) sub-models — must be defined before TenantReportResponse
# ------------------------------------------------------------------


class ActiveVehicle(BaseModel):
    patente: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    fiscalValue: Optional[int] = None


class ActiveProperty(BaseModel):
    address: Optional[str] = None
    comuna: Optional[str] = None
    fiscalValue: Optional[int] = None
    rol: Optional[str] = None


class ActivesData(BaseModel):
    vehicles: List[ActiveVehicle] = Field(default_factory=list)
    properties: List[ActiveProperty] = Field(default_factory=list)


class TenantReportResponse(BaseModel):
    """Tenant (or company) risk report returned by HomeSpotter `/get_tenant_report`."""

    issuerCompanyData: Optional[IssuerCompanyData | Dict[str, Any]] = None
    tenantReportID: Optional[str] = None
    tenantReportDate: Optional[str] = None
    reportType: Optional[str] = None
    name: Optional[str] = None
    rut: Optional[str] = None
    address: Optional[str] = None
    sales: Optional[str] = None
    economicActivity: Optional[str] = None
    activitiesStartDate: Optional[str] = None
    industry: Optional[str] = None
    companyType: Optional[str] = None
    companySubType: Optional[str] = None
    workers: Optional[int] = None
    foundationYear: Optional[int] = None
    web: Optional[str | List[str]] = None

    partners: Optional[Dict[str, Any]] = Field(default_factory=dict)
    societies: List[Dict[str, Any]] = Field(default_factory=list)
    actives: Optional[ActivesData] = Field(default_factory=ActivesData)
    taxActivities: List[Dict[str, Any]] = Field(default_factory=list)
    alertBulletin: List[Dict[str, Any]] = Field(default_factory=list)
    paymentsBulletin: Optional[Dict[str, Any]] = Field(default_factory=dict)
    laborBulletin: Optional[Dict[str, Any]] = Field(default_factory=dict)
    penaltyCauses: List[Dict[str, Any]] = Field(default_factory=list)
    finesDT: List[Dict[str, Any]] = Field(default_factory=list)
    pensionArrearsDT: List[Dict[str, Any]] = Field(default_factory=list)

    riskScore: Optional[int] = None
    actualDebts: List[Dict[str, Any]] = Field(default_factory=list)
    pdfUrl: Optional[str] = None

    class Config:
        orm_mode = True