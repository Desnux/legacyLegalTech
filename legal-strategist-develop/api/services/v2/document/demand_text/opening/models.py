from pydantic import Field

from models.pydantic import (
    Attorney,
    Creditor,
    Defendant,
    LegalRepresentative,
    Litigant,
    Plaintiff,
)
from services.v2.document.base import InformationBaseModel, InputBaseModel, OutputBaseModel


class DemandTextOpeningStructure(InformationBaseModel):
    """Demand text opening structure."""
    content: str | None = Field(None, description="Opening as raw text")


class DemandTextOpeningGeneratorInput(InputBaseModel):
    """Demand text opening generator input."""
    co_debtors: list[Defendant] | None = Field(None, description="Co-debtors to describe")
    creditor: Creditor | Plaintiff | None = Field(None, description="Creditor to describe")
    debtors: list[Defendant] | None = Field(None, description="Debtors to describe")
    document_count: int | None = Field(None, description="Amount of documents the demand argues about")
    legal_representatives: list[LegalRepresentative] | None = Field(None, description="Legal representatives of the creditor")
    smart: bool | None = Field(None, description="Whether to use AI or not")
    sponsoring_attorneys: list[Litigant | Attorney] | None = Field(None, description="Sponsoring attorneys to describe")


class DemandTextOpeningGeneratorOutput(OutputBaseModel[DemandTextOpeningStructure]):
    """Demand text opening generator output."""
