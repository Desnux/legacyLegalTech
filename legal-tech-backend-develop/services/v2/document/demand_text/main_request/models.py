from pydantic import Field

from models.pydantic import (
    CurrencyType,
    Defendant,
)
from services.v2.document.base import InformationBaseModel, InputBaseModel, OutputBaseModel


class DemandTextMainRequestStructure(InformationBaseModel):
    """Demand text main request structure."""
    content: str | None = Field(None, description="Main request as raw text")


class DemandTextMainRequestGeneratorInput(InputBaseModel):
    """Demand text main request generator input."""
    amount: int | None = Field(None, description="Amount in dispute")
    amount_currency: CurrencyType | None = Field(None, description="Amount currency")
    co_debtors: list[Defendant] | None = Field(None, description="Co-debtors to describe")
    debtors: list[Defendant] | None = Field(None, description="Debtors to describe")
    smart: bool | None = Field(None, description="Whether to use AI or not")


class DemandTextMainRequestGeneratorOutput(OutputBaseModel[DemandTextMainRequestStructure]):
    """Demand text main request generator output."""
