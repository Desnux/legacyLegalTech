from typing import Optional

from pydantic import BaseModel, Field


class Creditor(BaseModel):
    name: Optional[str] = Field(None, description="Name of the creditor or emitter")
    identifier: Optional[str] = Field(None, description="RUT or C.I.Nº of the creditor in the format XX.XXX.XXX-X or X.XXX.XXX-X")

    def normalize(self) -> None:
        if self.identifier:
            if len(self.identifier) > 2:
                self.identifier = self.identifier[:-2].replace("-", ".") + "-" + self.identifier[-2 + 1:].lower()