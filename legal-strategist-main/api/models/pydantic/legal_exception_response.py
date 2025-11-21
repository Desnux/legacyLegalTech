from datetime import date

from pydantic import BaseModel, Field
from .attorney import Attorney
from .defendant import Defendant
from .enum import LegalExceptionRequest
from .plaintiff import Plaintiff


class LegalExceptionResponseRequest(BaseModel):
    nature: LegalExceptionRequest = Field(..., description="Nature of the legal request")
    context: str | None = Field(None, description="Context behind the legal request")


class LegalExceptionResponse(BaseModel):
    summary: str | None = Field(None, description="Summary of the requests")
    court: str | None = Field(None, description="Indicates the court to which the response is addressed")
    opening: str | None = Field(None, description="Opening of the response")
    exception_responses: list[str] | None = Field(None, description="Responses to every exception raised")
    main_request: str | None = Field(None, description="Main request of the compromise")
    additional_requests: str | None = Field(None, description="Additional requests of the compromise")

    def to_raw_text(self) -> str | None:
        segments = filter(None, [
            self.summary,
            self.court,
            self.opening,
            "\n\n".join(self.exception_responses) if self.exception_responses else None,
            self.main_request,
            self.additional_requests,
        ])
        return "\n\n".join(segments) if segments else None


class LegalExceptionResponseInput(BaseModel):
    suggestion: str | None = Field(None, description="Response suggestion")
    case_title: str | None = Field(None, description="Legal case title")
    case_role: str | None = Field(None, description="Role of the legal case")
    court_city: str | None = Field(None, description="City where the court is located, in titlecase")
    court_number: int | None = Field(None, description="Court number, if any, None otherwise")
    request_date: date | None = Field(None, description="Date of the exceptions this request answers to")
    plaintiffs: list[Plaintiff] | None = Field(None, description="Plaintiffs in the legal case")
    sponsoring_attorneys: list[Attorney] | None = Field(None, description="Attorneys for the plaintiffs involved in the response")
    defendants: list[Defendant] | None = Field(None, description="Defendants in the legal case")
    defendant_attorneys: list[Attorney] | None = Field(None, description="Attorneys for the defendants involved in the response")
    secondary_requests: list[LegalExceptionResponseRequest] | None = Field(None, description="Secondary requests that apply to the compromise")
