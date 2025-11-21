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
    creation_date: date | None = Field(None, description="Creation date of the bill")
    due_payment_date: date | None = Field(None, description="Due date for paying the total amount")
    creditors: list[Creditor] | None = Field(None, description="Creditors or emitters of the bill")
    debtors: list[Debtor] | None = Field(None, description="Main debtors or suscribers of the bill")
    city: str | None = Field(None, description="City where the bill was made or signed")

    def normalize(self) -> None:
        for creditor in self.creditors or []:
            creditor.normalize()
        for debtor in self.debtors or []:
            debtor.normalize()
    
    def get_simple_dict(self) -> dict:
        dictionary = self.model_dump()
        dictionary["creditors"] = list(map(lambda x: {"name": x.name, "identifier": x.identifier}, self.creditors or []))
        dictionary["debtors"] = list(map(lambda x: {"name": x.name, "identifier": x.identifier}, self.debtors or []))
        return dictionary


class BillExtractorInput(ExtractorInputBaseModel):
    """Bill extractor input."""


class BillExtractorOutput(OutputBaseModel[BillInformation]):
    """Bill extractor output."""
