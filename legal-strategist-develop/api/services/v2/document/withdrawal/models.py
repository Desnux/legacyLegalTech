from pydantic import Field

from models.pydantic import Attorney, Plaintiff, Defendant
from services.v2.document.base import InformationBaseModel, InputBaseModel, OutputBaseModel


class WithdrawalStructure(InformationBaseModel):
    """Withdrawal structure."""
    header: str | None = Field(None, description="Withdrawal header")
    summary: str | None = Field(None, description="Withdrawal summary")
    court: str | None = Field(None, description="Court the withdrawal is addressed to")
    content: str | None = Field(None, description="Withdrawal explanation")
    main_request: str | None = Field(None, description="Withdrawal request to the court")


class WithdrawalGeneratorInput(InputBaseModel):
    """Withdrawal generator input."""
    case_role: str | None = Field(None, description="Role of the legal case")
    case_title: str | None = Field(None, description="Legal case title")
    court_city: str | None = Field(None, description="City where the court is located, in titlecase")
    court_number: int | None = Field(None, description="Court number, if any, None otherwise")
    plaintiffs: list[Plaintiff] | None = Field(None, description="Plaintiffs in the legal case")
    sponsoring_attorneys: list[Attorney] | None = Field(None, description="Attorneys for the plaintiffs involved in the response")
    co_debtors: list[Defendant] | None = Field(None, description="Co-debtors in the legal case")
    debtors: list[Defendant] | None = Field(None, description="Debtors in the legal case")
    suggestion: str | None = Field(None, description="Suggestion to guide withdrawal content and request generation")
    legal_article: str | None = Field(None, description="Legal article that allows the withdrawal")


class WithdrawalGeneratorOutput(OutputBaseModel[WithdrawalStructure]):
    """Withdrawal generator output."""
