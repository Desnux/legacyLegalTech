from pydantic import Field

from models.pydantic import Attorney, JudicialCollectionDemandExceptionRequest
from services.v2.document.base import ExtractorInputBaseModel, InformationBaseModel, OutputBaseModel


class DemandExceptionInformation(InformationBaseModel):
    """Demand exception information."""
    court_city: str | None = Field(None, description="City where the court is located")
    court_number: int | None = Field(None, description="Number the court, if any")
    case_role: str | None = Field(None, description="Role assigned to the case, includes its year")
    case_title: str | None = Field(None, description="Title assigned to the case")
    attorneys: list[Attorney] | None = Field(None, description="Defendant attorneys information")
    exceptions: list[JudicialCollectionDemandExceptionRequest] | None = Field(None, description="List of raised exceptions")


class DemandExceptionExtractorInput(ExtractorInputBaseModel):
    """Demand exception extractor input."""


class DemandExceptionExtractorOutput(OutputBaseModel[DemandExceptionInformation]):
    """Demand exception extractor output."""
