from pydantic import BaseModel, Field


class HearingInformation(BaseModel):
    hearing_hour: str | None = Field(None, description="Hour set for the hearing, if any, in 24 hours mm:hh format")
    hearing_days: list[int] | None = Field(None, description="Days set for the hearing, if any, as numbers relative to the probation period, for example: 'los dos últimos días del probatorio' -> [-2, -1]; 'el día octavo o noveno del probatorio' -> [8, 9]")
