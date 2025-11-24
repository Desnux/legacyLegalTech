from pydantic import BaseModel, Field


class Litigant(BaseModel):
    name: str | None = Field(None, description="Litigant name")
    identifier: str | None = Field(None, description="Litigant RUT or C.I.Nº")
    legal_representatives: list["Litigant"] | None = Field(None, description="Legal representatives of the litigant")
