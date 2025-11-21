from datetime import date
from pydantic import Field

from models.pydantic import (
    Creditor,
    Debtor,
    CurrencyType,
    Frequency,
)
from services.v2.document.base import ExtractorInputBaseModel, InformationBaseModel, OutputBaseModel


class PromissoryNoteInformation(InformationBaseModel):
    """Promissory note information."""
    identifier: str | None = Field(None, description="Number that identifies the promissory note")
    amount: int | None = Field(None, description="Amount to pay")
    amount_currency: CurrencyType | None = Field(None, description="Currency of the amount")
    creation_date: date | None = Field(None, description="Creation date of the promissory note")
    payment_installments: int | None = Field(None, description="Number of installments with which to pay the amount")
    payment_frequency: Frequency | None = Field(None, description="Payment frequency, either 'monthly' or 'annually'")
    amount_per_installment: int | None = Field(None, description="Amount to pay for each or most installments")
    amount_last_installment: int | None = Field(None, description="Amount to pay for the last installment")
    due_payment_day: int | None = Field(None, description="Due day of the month for paying each or most installments")
    first_installment_date: date | None = Field(None, description="Due date for paying the first installment")
    last_installment_date: date | None = Field(None, description="Due date for paying the last installment")
    interest_rate: float | None = Field(None, description="Interest rate")
    interest_rate_frequency: Frequency | None = Field(None, description="Interest rate frequency, either 'monthly' or 'annually'")
    interest_rate_base_days: int | None = Field(None, description="Base used to calculate the interest rate frequency days")
    creditors: list[Creditor] | None = Field(None, description="Creditors or emitters of the promissory note")
    debtors: list[Debtor] | None = Field(None, description="Main debtors or suscribers of the promissory note")
    co_debtors: list[Debtor] | None = Field(None, description="Guaranteers or joint co-debtors of the promissory note")
    city: str | None = Field(None, description="City where the promissory note was made or signed")

    def normalize(self) -> None:
        for creditor in self.creditors or []:
            creditor.normalize()
        for debtor in self.debtors or []:
            debtor.normalize()
        for co_debtor in self.co_debtors or []:
            co_debtor.normalize()
    
    def get_simple_dict(self) -> dict:
        dictionary = self.model_dump()
        dictionary["creditors"] = list(map(lambda x: {"name": x.name, "identifier": x.identifier}, self.creditors or []))
        dictionary["debtors"] = list(map(lambda x: {"name": x.name, "identifier": x.identifier}, self.debtors or []))
        dictionary["co_debtors"] = list(map(lambda x: {"name": x.name, "identifier": x.identifier}, self.co_debtors or []))
        return dictionary


class PromissoryNoteExtractorInput(ExtractorInputBaseModel):
    """Promissory note extractor input."""


class PromissoryNoteExtractorOutput(OutputBaseModel[PromissoryNoteInformation]):
    """Promissory note extractor output."""
