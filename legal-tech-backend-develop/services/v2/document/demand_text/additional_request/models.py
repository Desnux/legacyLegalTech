from pydantic import Field

from models.pydantic import (
    Attorney,
    Creditor,
    JudicialCollectionLegalRequest,
    MissingPaymentDocumentType,
    Plaintiff,
)
from services.v2.document.base import InformationBaseModel, InputBaseModel, OutputBaseModel


class DemandTextAdditionalRequestStructure(InformationBaseModel):
    """Demand text additional request structure."""
    content: str | None = Field(None, description="Additional request as raw text")


class DemandTextAdditionalRequestGeneratorInput(InputBaseModel):
    """Demand text additional request generator input."""
    context: str | None = Field(None, description="Context used to generate smart request description")
    creditor: Creditor | Plaintiff | None = Field(None, description="Creditor to describe")
    document_types: list[MissingPaymentDocumentType] | None = Field(None, description="Missing payment files")
    nature: JudicialCollectionLegalRequest | None = Field(None, description="Nature of the request to describe")
    sponsoring_attorneys: list[Attorney] | None = Field(None, description="Sponsoring attorneys to describe")


class DemandTextAdditionalRequestGeneratorOutput(OutputBaseModel[DemandTextAdditionalRequestStructure]):
    """Demand text additional request generator output."""
