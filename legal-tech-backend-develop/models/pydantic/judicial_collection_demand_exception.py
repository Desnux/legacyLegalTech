import json
from datetime import date

from pydantic import BaseModel, Field, model_validator

from .legal_exception import LegalException

from .attorney import Attorney
from .defendant import Defendant
from .enum import LegalExceptionRequest
from .plaintiff import Plaintiff


class DemandExceptionStructure(BaseModel):
    header: str | None = Field(None, description="Demand exception header")
    opening: str | None = Field(None, description="Demand exception opening statement")
    summary: str | None = Field(None, description="Demand exception summary")
    exceptions: str | None = Field(None, description="Demand exceptions")
    main_request: str | None = Field(None, description="Demand exception main request")
    additional_requests: str | None = Field(None, description="Demand exception additional requests")

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

    def to_raw_text(self) -> str | None:
        segments = filter(None, [
            self.header,
            self.opening,
            self.summary,
            "S.J.L.",
            self.exceptions,
            self.main_request,
            self.additional_requests,
        ])
        return "\n\n".join(segments) if segments else None


class JudicialCollectionDemandException(BaseModel):
    text: str | None = Field(None, description="Text of exceptions related to a judicial collection")


class JudicialCollectionDemandExceptionSecondaryRequest(BaseModel):
    nature: LegalExceptionRequest = Field(..., description="Nature of the legal request")
    context: str | None = Field(None, description="Context behind the legal request")


class JudicialCollectionDemandExceptionRequest(BaseModel):
    nature: LegalException = Field(..., description="Nature of the legal exception")
    context: str | None = Field(None, description="Context behind the legal exception")


class JudicialCollectionDemandExceptionInput(BaseModel):
    court_city: str | None = Field(None, description="City where the court is located", max_length=64)
    court_number: int | None = Field(None, description="Number the court, if any")
    case_role: str | None = Field(None, description="Role assigned to the case, includes its year", max_length=32)
    case_title: str | None = Field(None, description="Title assigned to the case", max_length=256)
    plaintiffs: list[Plaintiff] | None = Field(None, description="Plaintiffs or ejecutantes that want to start the case")
    plaintiff_attorneys: list[Attorney] | None = Field(None, description="Plaintiff attorneys for the plaintiffs or ejecutantes")
    defendants: list[Defendant] | None = Field(None, description="Defendants or ejecutados the case is against")
    defendant_attorneys: list[Attorney] | None = Field(None, description="Defendant attorneys for the defendants or ejecutados")
    demand_text_date: date | None = Field(None, description="Demand text date of creation")
    exceptions: list[JudicialCollectionDemandExceptionRequest] | None = Field(None, description="Exceptions against the demand text that originated the case")
    secondary_requests: list[JudicialCollectionDemandExceptionSecondaryRequest] | None = Field(None, description="Secondary requests that apply to the text of exceptions")

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

class JudicialCollectionDemandExceptionPartial(BaseModel):
    partial_text: str | None = Field(..., description="A segment of a text of exceptions related to a judicial collection. This segment will be concatenated with the previous one, so it should be structured in a way that ensures smooth concatenation.")
