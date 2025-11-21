from datetime import date

from pydantic import BaseModel, Field
from .attorney import Attorney


class LegalResponse(BaseModel):
    header: str | None = Field(None, description="Indicates kind of legal response")
    court: str | None = Field(None, description="Indicates the court to which the response is addressed")
    response: str | None = Field(None, description="Body of the response")
    request: str | None = Field(None, description="Request that follows the response, may be None")

    def to_raw_text(self) -> str | None:
        segments = filter(None, [
            self.header,
            self.court,
            self.response,
            self.request,
        ])
        return "\n\n".join(segments) if segments else None


class LegalResponseInput(BaseModel):
    suggestion: str | None = Field(None, description="Response suggestion")
    case_title: str | None = Field(None, description="Legal case title")
    case_role: str | None = Field(None, description="Role of the legal case")
    court_city: str | None = Field(None, description="City where the court is located, in titlecase")
    court_number: int | None = Field(None, description="Court number, if any, None otherwise")
    request_date: date | None = Field(None, description="Date of the response this request answers to")
    attorneys: list[Attorney] | None = Field(None, description="Attorneys involved in the response")
    request: str | None = Field(None, description="Additional brief request that follows the response, may be None")
