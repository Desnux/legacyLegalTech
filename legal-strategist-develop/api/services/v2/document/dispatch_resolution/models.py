from datetime import date
from pydantic import Field

from services.v2.document.base import ExtractorInputBaseModel, InformationBaseModel, OutputBaseModel


class DispatchResolutionInformation(InformationBaseModel):
    """Dispatch resolution information."""
    court_city: str | None = Field(None, description="City where the court is located")
    court_number: int | None = Field(None, description="Number the court, if any")
    case_role: str | None = Field(None, description="Role assigned to the case, includes its year")
    case_title: str | None = Field(None, description="Title assigned to the case")
    resolution_date: date | None = Field(None, description="Dispatch resolution date")
    resolution: str | None = Field(None, description="Court resolution content")


class DispatchResolutionExtractorInput(ExtractorInputBaseModel):
    """Dispatch resolution extractor input."""


class DispatchResolutionExtractorOutput(OutputBaseModel[DispatchResolutionInformation]):
    """Dispatch resolution extractor output."""
