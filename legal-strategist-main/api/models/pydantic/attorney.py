from pydantic import BaseModel, Field


class Attorney(BaseModel):
    name: str | None = Field(None, description="Name of the attorney")
    identifier: str | None = Field(None, description="RUT or C.I.Nº of the attorney in the format XX.XXX.XXX-X or X.XXX.XXX-X")
    address: str | None = Field(None, description="Address of the attorney")

    def normalize(self) -> None:
        if self.identifier:
            if len(self.identifier) > 2:
                self.identifier = self.identifier[:-2].replace("-", ".") + "-" + self.identifier[-2 + 1:].lower()
