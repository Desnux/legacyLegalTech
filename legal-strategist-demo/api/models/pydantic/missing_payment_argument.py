from typing import Optional

from pydantic import BaseModel, Field

from .enum import MissingPaymentDocumentType


class MissingPaymentArgument(BaseModel):
    argument: Optional[str] = Field(..., description="Legal argument related to a missing payment")
    document_type: Optional[MissingPaymentDocumentType] = Field(None, description="Document type of the source of the argument")


class MissingPaymentArgumentPartial(BaseModel):
    partial_argument: Optional[str] = Field(..., description="A segment of a legal argument related to a missing payment. This segment will be concatenated with the previous one, so it should be structured in a way that ensures smooth concatenation.")


class MissingPaymentArgumentReason(BaseModel):
    reason: Optional[str] = Field(..., description="Reason related to a missing payment, does not include specific money amounts")
    pending_amount: Optional[int] = Field(None, description="Pending total amount to pay, may be null if not provided")
    capital_amount: Optional[int] = Field(None, description="Pending sub-amount that corresponds to capital, may be null if not provided")
    interest_amount: Optional[int] = Field(None, description="Pending sub-amount that corresponds to interests, may be null if not provided")
    debt_amount: Optional[int] = Field(None, description="Pending sub-amount that corresponds to debts or late payment fees, may be null if not provided")
