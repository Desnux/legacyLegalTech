from pydantic import Field

from models.pydantic import CurrencyType
from services.v2.document.base import InformationBaseModel, InputBaseModel, OutputBaseModel
from services.v2.document.coopeuch_report import ClaimantPartner, ClaimantRequest, Transaction
from .input import MeasureInformation


class PreliminaryMeasureStructure(InformationBaseModel):
    """Preliminary measure structure."""


class PreliminaryMeasureGeneratorInput(InputBaseModel):
    """Preliminary measure generator input."""
    measure_information: MeasureInformation | None = Field(None, description="Information not extracted from a report")
    city: str | None = Field(None, description="City where the complaint was made")
    total_transaction_amount: float | None = Field(None, description="Total monetary amount of all claimed transactions, as number")
    currency_type: CurrencyType | None = Field(CurrencyType.CLP, description="Currency type of the total amount, either 'clp', 'usd', or 'uf'")
    claimed_transactions: list[Transaction] | None = Field([], description="Claimed transactions")
    claimant_partner: ClaimantPartner | None = Field(None, description="Claimant partner information")
    claimant_request: ClaimantRequest | None = Field(None, description="Claimant request information")


class PreliminaryMeasureGeneratorOutput(OutputBaseModel[PreliminaryMeasureStructure]):
    """Preliminary measure generator output."""
    pdf_bytes: bytes | None = Field(None, description="PDF raw bytes")
