import logging
from datetime import date
from pydantic import Field

from models.pydantic import (
    Creditor,
    CurrencyType,
    Debtor,
)
from services.v2.document.base import ExtractorInputBaseModel, InformationBaseModel, OutputBaseModel


class BillInformation(InformationBaseModel):
    """Bill information."""
    identifier: int | None = Field(None, description="Number that identifies the bill")
    amount: int | None = Field(None, description="Total amount to pay")
    amount_currency: CurrencyType | None = Field(None, description="Currency of the amount, defaults to 'clp'")
    handwritten_amount: bool | None = Field(None, description="Whether the amount is handwritten or not")
    creation_date: date | None = Field(None, description="Creation date of the bill")
    due_payment_date: date | None = Field(None, description="Due date for paying the total amount")
    creditors: list[Creditor] | None = Field(None, description="Creditors or emitters of the bill")
    debtors: list[Debtor] | None = Field(None, description="Main debtors or suscribers of the bill")
    city: str | None = Field(None, description="City where the bill was made or signed")

    def normalize(self) -> None:
        try:
            if self.creditors:
                for creditor in self.creditors:
                    creditor.normalize()
            if self.debtors:
                for debtor in self.debtors:
                    debtor.normalize()
        except Exception as normalize_error:
            logging.error(f"  ❌ [BillInformation] Error en normalize(): {type(normalize_error).__name__}: {normalize_error}")
            import traceback
            logging.error(f"  📋 [BillInformation] Stack trace: {traceback.format_exc()}")
            raise
    
    def get_simple_dict(self) -> dict:
        dictionary = self.model_dump()
        dictionary["creditors"] = list(map(lambda x: {"name": x.name, "identifier": x.identifier}, self.creditors or []))
        dictionary["debtors"] = list(map(lambda x: {"name": x.name, "identifier": x.identifier}, self.debtors or []))
        return dictionary


class BillExtractorInput(ExtractorInputBaseModel):
    """Bill extractor input."""


class BillExtractorOutput(OutputBaseModel[BillInformation]):
    """Bill extractor output."""
