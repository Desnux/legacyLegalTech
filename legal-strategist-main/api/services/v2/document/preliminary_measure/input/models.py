from datetime import date
from fastapi import UploadFile
from pydantic import Field

from models.pydantic import CurrencyType
from services.v2.document.base import InformationBaseModel, InputBaseModel, OutputBaseModel
from services.v2.document.coopeuch_report import ClaimantPartner, ClaimantRequest, Transaction


class MeasureInformation(InputBaseModel):
    """Additional measure information."""
    local_police_number: int | None = Field(None, description="Local police station number, if any")
    communication_date: date | None = Field(None, description="Communication to the client date")
    coopeuch_registry_uri: str | None = Field(None, description="COOPEUCH registry image uri")
    transaction_to_self_uri: str | None = Field(None, description="Transaction to self account image uri")
    payment_to_account_uri: str | None = Field(None, description="Payment to user account image uri")
    user_report_uri: str | None = Field(None, description="User report to police image uri")
    safesigner_report_uri: str | None = Field(None, description="Safesigner report image uri")
    mastercard_connect_report_uri: str | None = Field(None, description="Mastercard Connect report image uri")
    celmedia_report_uri: str | None = Field(None, description="CELMEDIA report image uri")


class PreliminaryMeasureInputInformation(InformationBaseModel):
    """Preliminary measure input information."""
    measure_information: MeasureInformation | None = Field(None, description="Information not extracted from a report")
    city: str | None = Field(None, description="City where the complaint was made")
    total_transaction_amount: float | None = Field(None, description="Total monetary amount of all claimed transactions, as number")
    currency_type: CurrencyType | None = Field(CurrencyType.CLP, description="Currency type of the total amount, either 'clp', 'usd', or 'uf'")
    claimed_transactions: list[Transaction] | None = Field([], description="Claimed transactions")
    claimant_partner: ClaimantPartner | None = Field(None, description="Claimant partner information")
    claimant_request: ClaimantRequest | None = Field(None, description="Claimant request information")


class PreliminaryMeasureInputExtractorInput(InputBaseModel):
    """Preliminary measure input extractor input."""
    file: UploadFile | None = Field(None, description="COOPEUCH report file")
    local_police_number: int | None = Field(None, description="Local police station number, if any")
    communication_date: date | None = Field(None, description="Communication to the client date")
    coopeuch_registry_uri: str | None = Field(None, description="COOPEUCH registry image uri")
    transaction_to_self_uri: str | None = Field(None, description="Transaction to self account image uri")
    payment_to_account_uri: str | None = Field(None, description="Payment to user account image uri")
    user_report_uri: str | None = Field(None, description="User report to police image uri")
    safesigner_report_uri: str | None = Field(None, description="Safesigner report image uri")
    mastercard_connect_report_uri: str | None = Field(None, description="Mastercard Connect report image uri")
    celmedia_report_uri: str | None = Field(None, description="CELMEDIA report image uri")


class PreliminaryMeasureInputExtractorOutput(OutputBaseModel[PreliminaryMeasureInputInformation]):
    """Preliminary measure input extractor output."""
