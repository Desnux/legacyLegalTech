import json
from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from .analysis import Analysis
from .attorney import Attorney
from .bill import Bill
from .correction import CorrectionField, CorrectionFieldList
from .creditor import Creditor
from .debtor import Debtor
from .defendant import Defendant
from .enum import CurrencyType, LegalSubject
from .legal_representative import LegalRepresentative
from .locale import Locale
from .judicial_collection_legal_request import JudicialCollectionLegalRequest
from .missing_payment_argument import MissingPaymentArgument
from .pjud import PJUDABDTE, PJUDDDO, PJUDDTE
from .plaintiff import Plaintiff
from .promissory_note import PromissoryNote


class CorrectionSecondaryRequest(str, Enum):
    INCLUDE_DOCUMENTS = "include_documents"
    OTHER = "other"

    def get_prompt(self, context: str, data: dict, locale: Locale) -> str:
        prompt = f"Generate a formal legal statement in {locale} that conveys instructions or obligations using an impersonal tone, "
        prompt += f"formal legal vocabulary, and complex sentence structure. The language should reflect a high level of authority and precision, similar to how official legal documents are written."
        if self == CorrectionSecondaryRequest.INCLUDE_DOCUMENTS:
            prompt += f"\nConsider the following template, localize it and modify it as you see fit: <template>RUEGO A US. tener por acompañados los documentos ...</template>"
            prompt += f"\nConsider the following context and data to fill in the documents: <data>{data}</data> <context>{context}</context>"
        else:
            prompt += f"\nIt should be legal request to a court inside a demand text about the following context: <context>{context}</context>"
            prompt += f"\nConsider the following template, localize it and modify it as you see fit: <template>RUEGO A US. tener presente ...</template>"
        prompt += "When answering:\n-If you lack context or data, omit and adjust text around, do not use example information."
        return prompt

    def to_localized_string(self, locale: Locale) -> str:
        if locale == Locale.ES_ES:
            if self == CorrectionSecondaryRequest.INCLUDE_DOCUMENTS:
                return "ACOMPAÑA DOCUMENTOS"
        else:
            if self == CorrectionSecondaryRequest.INCLUDE_DOCUMENTS:
                return "INCLUDE DOCUMENTS"
        return self.value


class DemandTextCorrectionSecondaryRequest(str, Enum):
    nature: CorrectionSecondaryRequest = Field(..., description="Nature of the legal request")
    context: str | None = Field(..., description="Context behind the legal request")


class JudicialCollectionDemandText(BaseModel):
    text: Optional[str] = Field(..., description="Demand text related to a judicial collection")


class JudicialCollectionDemandTextExtractedInfo(BaseModel):
    creditors: Optional[list[Creditor]] = Field(..., description="Unique creditors or emitters across payment documents")
    debtors: Optional[list[Debtor]] = Field(..., description="Unique debtors across payment documents")
    defendants: Optional[list[Defendant]] = Field(..., description="Unique debtors and co-debtors across payment documents")
    co_debtors: Optional[list[Debtor]] = Field(..., description="Unique co-debtors across payment documents")
    city: Optional[str] = Field(..., description="City where the payment documents were made or signed")
    amount: Optional[int] = Field(..., description="Total amount to pay across payment documents")
    amount_currency: Optional[CurrencyType] = Field(..., description="Currency of the total amount to pay")


class JudicialCollectionSecondaryRequest(BaseModel):
    nature: JudicialCollectionLegalRequest = Field(..., description="Nature of the legal request")
    context: Optional[str] = Field(None, description="Context behind the legal request")


class JudicialCollectionDemandTextInput(BaseModel):
    legal_subject: Optional[LegalSubject] = Field(None, description="Legal subject of the case behind the demand text")
    plaintiffs: Optional[list[Plaintiff]] = Field(None, description="Plaintiffs or claimants behind the demand text, may be None if unspecified")
    legal_representatives: Optional[list[LegalRepresentative]] = Field(None, description="Legal representatives of the plaintiffs")
    sponsoring_attorneys: Optional[list[Attorney]] = Field(None, description="Sponsoring attorneys for the plaintiffs")
    reasons_per_document: Optional[list[str]] = Field(None, description="List of reasons to argue about missing payments, zipped to a list of documents")
    main_request: Optional[str] = Field(None, description="Main request behind filing the demand text")
    secondary_requests: Optional[list[JudicialCollectionSecondaryRequest]] = Field(None, description="Secondary requests that apply to the demand text")

    def normalize(self) -> None:
        for plaintiff in self.plaintiffs or []:
            plaintiff.normalize()
        for attorney in self.sponsoring_attorneys or []:
            attorney.normalize()
        for legal_representative in self.legal_representatives or []:
            legal_representative.normalize()

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class JudicialCollectionDemandTextPartial(BaseModel):
    partial_text: Optional[str] = Field(..., description="A segment of a demand text related to a judicial collection. This segment will be concatenated with the previous one, so it should be structured in a way that ensures smooth concatenation.")


class JudicialCollectionDemandTextAnalysis(BaseModel):
    header: Analysis | None = Field(..., description="Demand text header analysis")
    summary: Analysis | None = Field(..., description="Demand text summary analysis")
    court: Analysis | None = Field(..., description="Demand text court info analysis")
    opening: Analysis | None = Field(..., description="Demand text opening paragraphs analysis")
    missing_payment_arguments: list[Analysis] | None = Field(..., description="Demant text missing payment arguments analysis")
    main_request: Analysis | None = Field(..., description="Demand text main request analysis")
    additional_requests: Analysis | None = Field(..., description="Demand text additional requests analysis")
    overall: Analysis | None = Field(..., description="Overall analysis of the demand text")


class JudicialCollectionDemandTextStructure(BaseModel):
    header: str | None = Field(..., description="Demand text header")
    summary: str | None = Field(..., description="Demand text summary")
    court: str | None = Field(..., description="Demand text court info")
    opening: str | None = Field(..., description="Demand text opening paragraphs")
    missing_payment_arguments: list[MissingPaymentArgument] | None = Field(..., description="Demant text missing payment arguments")
    main_request: str | None = Field(..., description="Demand text main request")
    additional_requests: str | None = Field(..., description="Demand text additional requests")
    sponsoring_attorneys: list[PJUDABDTE] | None = Field(None, description="Sponsoring attorneys for the plaintiffs in the demand text")
    plaintiffs: list[PJUDDTE] | None = Field(None, description="Plaintiffs in the demand text")
    defendants: list[PJUDDDO] | None = Field(None, description="Defendants in the demand text")
    legal_subject: LegalSubject | None = Field(None, description="Legal subject of the case behind the demand text")
    city: str | None = Field(None, description="City where the demand takes place")

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

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


class DemandTextCorrectionForm(BaseModel):
    defendants: list[list[CorrectionField | CorrectionFieldList]] = Field(..., description="Defendant information")
    plaintiffs: list[list[CorrectionField]] = Field(..., description="Plaintiff information")
    bills: list[list[CorrectionField]] = Field(..., description="Bill information")
    promissory_notes: list[list[CorrectionField]] = Field(..., description="Promissory note information")
    sponsoring_attorneys: list[list[CorrectionField]] = Field(..., description="Sponsoring attorney information")

    def update(self) -> None:
        for defendant in self.defendants:
            for field in defendant:
                field.update()
        for plaintiff in self.plaintiffs:
            for field in plaintiff:
                field.update()
        for bill in self.bills:
            for field in bill:
                field.update()
        for promissory_note in self.promissory_notes:
            for field in promissory_note:
                field.update()
        for sponsoring_attorney in self.sponsoring_attorneys:
            for field in sponsoring_attorney:
                field.update()

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class DemandTextCorrectionInformation(BaseModel):
    defendants: list[Defendant] | None = Field(None, description="Defendant information")
    plaintiffs: list[Plaintiff] | None = Field(None, description="Plaintiff information")
    bills: list[Bill] | None = Field(None, description="Bill information")
    promissory_notes: list[PromissoryNote] | None = Field(None, description="Promissory note information")
    sponsoring_attorneys: list[Attorney] | None = Field(None, description="Sponsoring attorney information")

    def get_as_form(self) -> DemandTextCorrectionForm:
        return DemandTextCorrectionForm(
            defendants=self.get_defendants_correction_fields(),
            plaintiffs=self.get_plaintiffs_correction_fields(),
            bills=self.get_bills_correction_fields(),
            promissory_notes=self.get_promissory_notes_correction_fields(),
            sponsoring_attorneys=self.get_sponsoring_attorneys_correction_fields(),
        )
    
    def get_defendants_correction_fields(self) -> list[list[CorrectionField | CorrectionFieldList]]:
        correction_fields: list[list[CorrectionField | CorrectionFieldList]] = []
        for defendant in self.defendants or []:
            correction_fields.append(defendant.get_correction_fields())
        return correction_fields

    def get_plaintiffs_correction_fields(self) -> list[list[CorrectionField]]:
        correction_fields: list[list[CorrectionField]] = []
        for plaintiff in self.plaintiffs or []:
            correction_fields.append(plaintiff.get_correction_fields())
        return correction_fields

    def get_bills_correction_fields(self) -> list[list[CorrectionField]]:
        correction_fields: list[list[CorrectionField]] = []
        for bill in self.bills or []:
            correction_fields.append(bill.get_correction_fields())
        return correction_fields

    def get_promissory_notes_correction_fields(self) -> list[list[CorrectionField]]:
        correction_fields: list[list[CorrectionField]] = []
        for promissory_note in self.promissory_notes or []:
            correction_fields.append(promissory_note.get_correction_fields())
        return correction_fields
    
    def get_sponsoring_attorneys_correction_fields(self) -> list[list[CorrectionField]]:
        correction_fields: list[list[CorrectionField]] = []
        for sponsoring_attorney in self.sponsoring_attorneys or []:
            correction_fields.append(sponsoring_attorney.get_correction_fields())
        return correction_fields


class DemandTextCorrection(BaseModel):
    summary: str | None = Field(None, description="Summary of the correction")
    court: str | None = Field(None, description="Indicates the court to which the correction is addressed")
    opening: str | None = Field(None, description="Preliminary information about the correction")
    corrections: str | None = Field(None, description="List of particular corrections")
    main_request: str | None = Field(..., description="Main request of the correction")
    additional_requests: str | None = Field(..., description="Additional requests of the correction")

    def to_raw_text(self) -> str | None:
        segments = filter(None, [
            self.summary,
            self.court,
            self.opening,
            self.corrections,
            self.main_request,
            self.additional_requests,
        ])
        return "\n\n".join(segments) if segments else None


class DemandTextCorrectionInput(BaseModel):
    suggestion: str | None = Field(None, description="Response suggestion")
    case_title: str | None = Field(None, description="Legal case title")
    case_role: str | None = Field(None, description="Role of the legal case")
    court_city: str | None = Field(None, description="City where the court is located, in titlecase")
    court_number: int | None = Field(None, description="Court number, if any, None otherwise")
    request_date: date | None = Field(None, description="Date of the response this correction answers to")
    attorneys: list[Attorney] | None = Field(None, description="Attorneys involved in the correction")
    secondary_requests: list[DemandTextCorrectionSecondaryRequest] | None = Field(None, description="Secondary requests that apply to the corrections")
