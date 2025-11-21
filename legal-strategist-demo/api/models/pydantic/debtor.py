from typing import Optional

from pydantic import BaseModel, Field

from .legal_representative import LegalRepresentative


class Debtor(BaseModel):
    name: Optional[str] = Field(None, description="Name of the debtor or suscriptor")
    identifier: Optional[str] = Field(None, description="RUT or C.I.Nº of the debtor or suscriptor in the format XX.XXX.XXX-X or X.XXX.XXX-X")
    address: Optional[str] = Field(None, description="Address of debtor or suscriptor")
    legal_representatives: Optional[list[LegalRepresentative]] = Field(None, description="Legal representatives of the debtor or suscriptor")

    def normalize(self) -> None:
        if self.identifier:
            if len(self.identifier) > 2:
                self.identifier = self.identifier[:-2].replace("-", ".") + "-" + self.identifier[-2 + 1:].lower()
                numeric_part = self.identifier[:-2].replace(".", "").strip()
                if numeric_part.isdigit() and int(numeric_part) < 50000000:
                    self.legal_representatives = None
        if self.legal_representatives:
            for rep in self.legal_representatives:
                rep.normalize()
