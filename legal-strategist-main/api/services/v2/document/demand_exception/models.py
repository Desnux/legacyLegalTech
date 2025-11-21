from pydantic import Field

from models.pydantic import Attorney, JudicialCollectionDemandExceptionRequest
from services.v2.document.base import ExtractorInputBaseModel, InformationBaseModel, OutputBaseModel


class DemandExceptionInformation(InformationBaseModel):
    """Demand exception information."""
    attorneys: list[Attorney] | None = Field(None, description="Defendant attorneys information")
    exceptions: list[JudicialCollectionDemandExceptionRequest] | None = Field(None, description="List of raised exceptions")


class DemandExceptionExtractorInput(ExtractorInputBaseModel):
    """Demand exception extractor input."""


class DemandExceptionExtractorOutput(OutputBaseModel[DemandExceptionInformation]):
    """Demand exception extractor output."""
