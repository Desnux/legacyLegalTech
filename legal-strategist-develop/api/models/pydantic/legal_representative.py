from pydantic import BaseModel, Field


class LegalRepresentative(BaseModel):
    name: str | None = Field(None, description="Name of the legal representative")
    identifier: str | None = Field(None, description="RUT or C.I.Nº of the legal representative in the format XX.XXX.XXX-X or X.XXX.XXX-X")
    occupation: str | None = Field(None, description="Occupation or profession of the legal representative")
    address: str | None = Field(None, description="Address of the legal representative")

    def normalize(self) -> None:
        if self.identifier:
            if len(self.identifier) > 2:
                self.identifier = self.identifier[:-2].replace("-", ".") + "-" + self.identifier[-2 + 1:].lower()
