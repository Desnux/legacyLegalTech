from pydantic import BaseModel, Field

from models.pydantic import (
    Creditor,
    MissingPaymentDocumentType,
    Plaintiff,
)
from services.v2.document.base import InformationBaseModel, InputBaseModel, OutputBaseModel
from services.v2.document.bill import BillInformation
from services.v2.document.promissory_note import PromissoryNoteInformation


class MissingPaymentArgumentReason(BaseModel):
    """Missing payment provided reason to argue."""
    reason: str = Field(..., description="Reason related to a missing payment, does not include specific money amounts")
    pending_amount: int | None = Field(None, description="Pending total amount to pay, may be null if not provided")
    capital_amount: int | None = Field(None, description="Pending sub-amount that corresponds to capital, may be null if not provided")
    interest_amount: int | None = Field(None, description="Pending sub-amount that corresponds to interests, may be null if not provided")
    debt_amount: int | None = Field(None, description="Pending sub-amount that corresponds to debts or late payment fees, may be null if not provided")


class MissingPaymentArgumentStructure(InformationBaseModel):
    """Missing payment argument structure."""
    argument: str | None = Field(None, description="Legal argument related to a missing payment")
    document_type: MissingPaymentDocumentType | None = Field(None, description="Source of the argument")


class MissingPaymentArgumentGeneratorInput(InputBaseModel):
    """Missing payment argument generator input."""
    document: BillInformation | PromissoryNoteInformation | None = Field(None, description="Document information")
    document_type: MissingPaymentDocumentType | None = Field(None, description="Document type")
    over_creditor: Creditor | Plaintiff | None = Field(None, description="Overrides creditor found in content")
    reason: str | None = Field(None, description="Reason to argue about a missing payment")
    structured_reason: MissingPaymentArgumentReason | None = Field(None, description="Structured to argue about a missing payment, overrided reason field")


class MissingPaymentArgumentGeneratorOutput(OutputBaseModel[MissingPaymentArgumentStructure]):
    """Missing payment argument generator output."""
    structured_reason: MissingPaymentArgumentReason | None = Field(None, description="Structured reason behind the argument")
