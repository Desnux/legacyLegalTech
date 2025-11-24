from pydantic import Field

from models.pydantic import (
    Attorney,
    Creditor,
    Defendant,
    LegalSubject,
    Litigant,
    Plaintiff,
)
from services.v2.document.base import InformationBaseModel, InputBaseModel, OutputBaseModel


class DemandTextHeaderStructure(InformationBaseModel):
    """Demand text header structure."""
    content: str | None = Field(None, description="Header as raw text")


class DemandTextHeaderGeneratorInput(InputBaseModel):
    """Demand text header generator input."""
    defendants: list[Defendant | Litigant] | None = Field(None, description="Defendants to enumerate")
    legal_subject: LegalSubject | None = Field(None, description="Legal subject")
    plaintiffs: list[Creditor | Litigant | Plaintiff] | None = Field(None, description="Plaintiffs to enumerate")
    sponsoring_attorneys: list[Attorney | Litigant] | None = Field(None, description="Sponsoring attorneys to enumerate")


class DemandTextHeaderGeneratorOutput(OutputBaseModel[DemandTextHeaderStructure]):
    """Demand text header generator output."""
