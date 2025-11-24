from pydantic import Field

from models.pydantic import (
    JudicialCollectionSecondaryRequest,
)
from services.v2.document.base import InformationBaseModel, InputBaseModel, OutputBaseModel


class DemandTextSummaryStructure(InformationBaseModel):
    """Demand text summary structure."""
    content: str | None = Field(None, description="Summary as raw text")


class DemandTextSummaryGeneratorInput(InputBaseModel):
    """Demand text summary generator input."""
    custom_summaries: list[tuple[int, str]] | None = Field(None, description="List of custom summaries for each request")
    secondary_requests: list[JudicialCollectionSecondaryRequest] | None = Field(None, description="Secondary requests to describe")


class DemandTextSummaryGeneratorOutput(OutputBaseModel[DemandTextSummaryStructure]):
    """Demand text summary generator output."""
    structured_summaries: list[tuple[int, str]] | None = Field(None, description="Summaries for each request")
