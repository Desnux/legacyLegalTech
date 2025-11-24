import json
from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from .attorney import Attorney
from .creditor import Creditor
from .debtor import Debtor
from .defendant import Defendant
from .enum import CurrencyType, LegalSubject
from .legal_representative import LegalRepresentative
from .locale import Locale
from .judicial_collection_legal_request import JudicialCollectionLegalRequest
from .plaintiff import Plaintiff


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

    def normalize(self) -> None:
        if self.context:
            self.context = self.context.strip() if self.context.strip() else None


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
