from enum import Enum
from pydantic import BaseModel, Field

from .legal_representative import LegalRepresentative


class DefendantType(str, Enum):
    DEBTOR = "debtor"
    CO_DEBTOR = "co_debtor"


class DefendantEntityType(str, Enum):
    NATURAL = "natural"
    LEGAL = "legal"


class Defendant(BaseModel):
    name: str | None = Field(None, description="Name of the defendant")
    identifier: str | None = Field(None, description="RUT or C.I.Nº of the defendant in the format XX.XXX.XXX-X or X.XXX.XXX-X")
    occupation: str | None = Field(None, description="Occupation or profession of the defendant")
    address: str | None = Field(None, description="Address of the legal defendant")
    legal_representatives: list[LegalRepresentative] | None = Field(None, description="Legal representatives of the defendant")
    type: DefendantType | None = Field(None, description="Type of defendant, either 'debtor' or 'co_debtor'")
    entity_type: DefendantEntityType | None = Field(None, description="Type of entity, either 'natural' for natural person or 'legal' for legal entity")

    def get_numeric_identifier(self) -> int:
        if self.identifier:
            numeric_part = self.identifier.replace('.', '').split('-')[0]
            try:
                value = int(numeric_part)
            except ValueError:
                return 0
            return value
        return 0

    def normalize(self) -> None:
        if self.identifier:
            if len(self.identifier) > 2:
                self.identifier = self.identifier[:-2].replace("-", ".") + "-" + self.identifier[-2 + 1:].lower()
                numeric_part = self.identifier[:-2].replace(".", "").strip()
                if numeric_part.isdigit() and int(numeric_part) < 50000000:
                    self.legal_representatives = None
                    self.entity_type = DefendantEntityType.NATURAL
                else:
                    self.entity_type = DefendantEntityType.LEGAL
        if self.legal_representatives:
            for rep in self.legal_representatives:
                rep.normalize()
