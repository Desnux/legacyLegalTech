from pydantic import BaseModel, Field

from models.pydantic import (
    Attorney,
    Creditor,
    CurrencyType,
    Defendant,
    MissingPaymentDocumentType,
    JudicialCollectionSecondaryRequest,
    LegalRepresentative,
    LegalSubject,
    MissingPaymentFile,
    Plaintiff,
)
from services.v2.document.base import InformationBaseModel, InputBaseModel, OutputBaseModel
from services.v2.document.bill import BillInformation
from services.v2.document.demand_text.missing_payment_argument import MissingPaymentArgumentReason
from services.v2.document.promissory_note import PromissoryNoteInformation


class DemandTextInputPartialInformation(BaseModel):
    """Demand text input partial information."""
    plaintiff: Plaintiff | None = Field(None, description="Plaintiff or claimant behind the demand text, may be None if unspecified")
    legal_representatives: list[LegalRepresentative] | None = Field(None, description="Legal representatives of the plaintiff")
    sponsoring_attorneys: list[Attorney] | None = Field(None, description="Sponsoring attorneys for the plaintiffs")
    main_request: str | None = Field(None, description="Main request behind filing the demand text")
    amount: int | None = Field(None, description="Total amount of money owned, if specified")
    secondary_requests: list[JudicialCollectionSecondaryRequest] | None= Field(None, description="Secondary requests that apply to the demand text")
    reasons_per_document: list[MissingPaymentArgumentReason] | None = Field(None, description="List of reasons to argue about missing payments, zipped to a list of documents")

    def normalize(self) -> None:
        for legal_representative in self.legal_representatives or []:
            legal_representative.normalize()
        if plaintiff := self.plaintiff:
            plaintiff.normalize()
        for secondary_request in self.secondary_requests or []:
            secondary_request.normalize()
        for sponsoring_attorney in self.sponsoring_attorneys or []:
            sponsoring_attorney.normalize()


class DemandTextInputInformation(InformationBaseModel):
    """Demand text input information."""
    amount: int | None = Field(None, description="Total amount to pay across payment documents")
    amount_currency: CurrencyType | None = Field(None, description="Currency of the total amount to pay")
    city: str | None = Field(None, description="City where the payment documents were made or signed")
    creditors: list[Creditor] | None = Field(None, description="Creditors or emitters across payment documents")
    defendants: list[Defendant] | None = Field(None, description="Debtors and co-debtors across payment documents")
    documents: list[BillInformation | PromissoryNoteInformation] | None = Field(None, description="Documents to argue about")
    document_types: list[MissingPaymentDocumentType] | None = Field(None, description="Document types")
    main_request: str | None= Field(None, description="Main request behind filing the demand text")
    plaintiff: Plaintiff | None = Field(None, description="Plaintiff or claimant behind the demand text, may be None if unspecified")
    legal_subject: LegalSubject | None = Field(None, description="Legal subject of the demand")
    legal_representatives: list[LegalRepresentative] | None = Field(None, description="Legal representatives of the plaintiff")
    reasons_per_document: list[MissingPaymentArgumentReason] | None = Field(None, description="List of reasons to argue about missing payments, zipped to documents")
    secondary_requests: list[JudicialCollectionSecondaryRequest] | None= Field(None, description="Secondary requests that apply to the demand text")
    sponsoring_attorneys: list[Attorney] | None = Field(None, description="Sponsoring attorneys for the plaintiffs")

    def normalize(self) -> None:
        for creditor in self.creditors or []:
            creditor.normalize()
        for defendant in self.defendants or []:
            defendant.normalize()
        for legal_representative in self.legal_representatives or []:
            legal_representative.normalize()
        if plaintiff := self.plaintiff:
            plaintiff.normalize()
        for secondary_request in self.secondary_requests or []:
            secondary_request.normalize()
        for sponsoring_attorney in self.sponsoring_attorneys or []:
            sponsoring_attorney.normalize()


class DemandTextInputExtractorInput(InputBaseModel):
    """Demand text input extractor input."""
    files: list[MissingPaymentFile] | None = Field(None, description="Files related to missing payment arguments")
    text: str | None = Field(None, description="Free form text information provided by an user")


class DemandTextInputExtractorOutput(OutputBaseModel[DemandTextInputInformation]):
    """Demand text input extractor output."""


class DemandTextUniqueLitigants(InformationBaseModel):
    """Demand text unique litigants."""
    creditors: list[Creditor] | None = Field(None, description="Unique creditors")
    defendants: list[Defendant] | None = Field(None, description="Unique debtors and co-debtors")
    sponsoring_attorneys: list[Attorney] | None = Field(None, description="Unique sponsoring attorneys")
