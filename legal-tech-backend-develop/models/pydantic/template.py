from pydantic import BaseModel, Field


class ExpandedFilledTemplate(BaseModel):
    result: str | None = Field(
        None,
        description="Result with all placeholder values replaced with real data, adjusted if necessary, and additional context included beyond the template, if given",
    )


class FilledTemplate(BaseModel):
    result: str | None = Field(None, description="Result with all placeholder values replaced with real data, adjusted if necessary")
