from pydantic import BaseModel, Field


class CourtInformation(BaseModel):
    court_city: str | None = Field(None, description="City where the court is located", max_length=64)
    court_number: int | None = Field(None, description="Number the court, if any")
    case_role: str | None = Field(None, description="Role assigned to the case, includes its year", max_length=32)
    case_title: str | None = Field(None, description="Title assigned to the case", max_length=256)
