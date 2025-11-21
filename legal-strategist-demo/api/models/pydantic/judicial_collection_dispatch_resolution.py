import json
from datetime import date

from pydantic import BaseModel, Field, model_validator

from .enum import JudicialCollectionLegalRequirement


class DispatchResolutionStructure(BaseModel):
    header: str | None = Field(None, description="Dispatch resolution header")
    date_line: str | None = Field(None, description="Dispatch resolution date line")
    resolution: str | None = Field(None, description="Court resolution")
    footer: str | None = Field(None, description="Dispatch resolution footer")
    city: str | None = Field(None, description="Origin city")
    readable_date: str | None = Field(None, description="Human readable date")

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

    def to_raw_text(self) -> str | None:
        segments = filter(None, [
            self.header,
            self.date_line,
            self.resolution,
            self.footer,
        ])
        return "\n\n".join(segments) if segments else None


class JudicialCollectionDispatchResolution(BaseModel):
    text: str | None = Field(..., description="Dispatch resolution related to a judicial collection")


class JudicialCollectionDispatchResolutionDate(BaseModel):
    human_readable_date: str | None = Field(..., description="Date as read aloud")


class JudicialCollectionDispatchRequirement(BaseModel):
    nature: JudicialCollectionLegalRequirement = Field(..., description="Nature of the legal requirement")
    context: str | None = Field(..., description="Context behind the legal requirement")


class JudicialCollectionDispatchResolutionInput(BaseModel):
    court_city: str | None = Field(None, description="City where the court is located", max_length=64)
    court_number: int | None = Field(None, description="Number the court, if any")
    case_role: str | None = Field(None, description="Role assigned to the case, includes its year", max_length=32)
    case_title: str | None = Field(None, description="Title assigned to the case", max_length=256)
    issue_date: date | None = Field(None, description="Date of issue")
    demand_text_date: date | None = Field(None, description="Demand text date of creation")
    requirements: list[JudicialCollectionDispatchRequirement] | None = Field(None, description="Requirements that must be resolved after the resolution")

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class JudicialCollectionDispatchResolutionPartial(BaseModel):
    partial_text: str | None = Field(..., description="A segment of a dispatch resolution related to a judicial collection. This segment will be concatenated with the previous one, so it should be structured in a way that ensures smooth concatenation.")
