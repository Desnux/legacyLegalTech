import json
from datetime import date

from pydantic import BaseModel, Field, model_validator


class LegalResolution(BaseModel):
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


class LegalResolutionInput(BaseModel):
    court_city: str | None = Field(None, description="City where the court is located", max_length=64)
    court_number: int | None = Field(None, description="Number the court, if any")
    case_role: str | None = Field(None, description="Role assigned to the case, includes its year", max_length=32)
    case_title: str | None = Field(None, description="Title assigned to the case", max_length=256)
    issue_date: date | None = Field(None, description="Date of issue")
    request_date: date | None = Field(None, description="Date of the request the resolution answers to")
    hearing_hour: str | None = Field(None, description="Hour set for the hearing")
    hearing_days: list[int] | None = Field(None, description="Days set for the hearing, if any, as numbers relative to the probation period")
