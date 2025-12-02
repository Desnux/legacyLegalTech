from uuid import UUID
from pydantic import Field

from models.pydantic import (
    Analysis,
    Attorney,
    Creditor,
    CurrencyType,
    Defendant,
    MissingPaymentDocumentType,
    JudicialCollectionSecondaryRequest,
    LegalRepresentative,
    LegalSubject,
    Plaintiff,
)
from services.v2.document.base import InformationBaseModel, InputBaseModel, OutputBaseModel
from services.v2.document.bill import BillInformation
from services.v2.document.demand_text.missing_payment_argument import MissingPaymentArgumentReason, MissingPaymentArgumentStructure
from services.v2.document.promissory_note import PromissoryNoteInformation


class DemandTextAnalysis(InformationBaseModel):
    """Demand text analysis."""
    header: Analysis | None = Field(..., description="Demand text header analysis")
    summary: Analysis | None = Field(..., description="Demand text summary analysis")
    court: Analysis | None = Field(..., description="Demand text court info analysis")
    opening: Analysis | None = Field(..., description="Demand text opening paragraphs analysis")
    missing_payment_arguments: list[Analysis] | None = Field(..., description="Demant text missing payment arguments analysis")
    main_request: Analysis | None = Field(..., description="Demand text main request analysis")
    additional_requests: Analysis | None = Field(..., description="Demand text additional requests analysis")
    overall: Analysis | None = Field(..., description="Overall analysis of the demand text")


class DemandTextStructure(InformationBaseModel):
    """Demand text structure."""
    header: str | None = Field(None, description="Demand text header")
    summary: str | None = Field(None, description="Demand text summary")
    court: str | None = Field(None, description="Demand text court info")
    opening: str | None = Field(None, description="Demand text opening paragraphs")
    missing_payment_arguments: list[MissingPaymentArgumentStructure] | None = Field(None, description="Demant text missing payment arguments")
    main_request: str | None = Field(None, description="Demand text main request")
    additional_requests: str | None = Field(None, description="Demand text additional requests")

    def to_raw_text(self) -> str | None:
        argument_segments = filter(None, self.missing_payment_arguments)
        segments = filter(None, [
            self.header,
            self.summary,
            self.court,
            self.opening,
            "\n\n".join(map(lambda x: x.argument, argument_segments)) if argument_segments else None,
            self.main_request,
            self.additional_requests,
        ])
        return "\n\n".join(segments) if segments else None


class DemandTextAnalyzerInput(InputBaseModel):
    """Demand text analyzer input."""
    header: str | None = Field(None, description="Demand text header")
    summary: str | None = Field(None, description="Demand text summary")
    court: str | None = Field(None, description="Demand text court info")
    opening: str | None = Field(None, description="Demand text opening paragraphs")
    missing_payment_arguments: list[MissingPaymentArgumentStructure] | None = Field(None, description="Demant text missing payment arguments")
    main_request: str | None = Field(None, description="Demand text main request")
    additional_requests: str | None = Field(None, description="Demand text additional requests")


class DemandTextAnalyzerOutput(OutputBaseModel[DemandTextAnalysis]):
    """Demand text generator output."""


class DemandTextGeneratorInput(InputBaseModel):
    """Demand text generator input."""
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


class DemandTextGeneratorOutput(OutputBaseModel[DemandTextStructure]):
    """Demand text generator output."""


class DemandTextSendResponse(InformationBaseModel):
    """Demand text send response."""
    message: str = Field(..., description="PJUD Response")
    status: int = Field(..., description="HTTP status code")
    case_id: UUID | None = Field(None, description="Case ID of the created case")


class DemandTextSenderInput(InputBaseModel):
    """Demand text sender input."""
    password: str = Field(..., description="PJUD Password")
    rut: str = Field(..., description="PJUD RUT")
    information: DemandTextGeneratorInput = Field(..., description="Demand text information")
    structure: DemandTextStructure = Field(..., description="Demand text structure")
    debug: bool = Field(False, description="Debug mode flag")
