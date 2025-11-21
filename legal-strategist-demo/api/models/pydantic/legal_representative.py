from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from .correction import CorrectionField, CorrectionFieldType


class LegalRepresentativeField(str, Enum):
    NAME = "name"
    IDENTIFIER = "identifier"
    OCCUPATION = "occupation"
    ADDRESS = "address"


class LegalRepresentative(BaseModel):
    name: Optional[str] = Field(None, description="Name of the legal representative")
    identifier: Optional[str] = Field(None, description="RUT or C.I.Nº of the legal representative in the format XX.XXX.XXX-X or X.XXX.XXX-X")
    occupation: Optional[str] = Field(None, description="Occupation or profession of the legal representative")
    address: Optional[str] = Field(None, description="Address of the legal representative")

    def normalize(self) -> None:
        if self.identifier:
            if len(self.identifier) > 2:
                self.identifier = self.identifier[:-2].replace("-", ".") + "-" + self.identifier[-2 + 1:].lower()

    def get_correction_fields(self) -> list[CorrectionField]:
        return [
            CorrectionField(
                label="Nombre",
                type=CorrectionFieldType.STRING,
                name=LegalRepresentativeField.NAME.value,
                initial_value=self.name,
                options=None,
            ),
            CorrectionField(
                label="Identificador",
                type=CorrectionFieldType.STRING,
                name=LegalRepresentativeField.IDENTIFIER.value,
                initial_value=self.identifier,
                options=None,
            ),
            CorrectionField(
                label="Ocupación",
                type=CorrectionFieldType.STRING,
                name=LegalRepresentativeField.OCCUPATION.value,
                initial_value=self.occupation,
                options=None,
            ),
            CorrectionField(
                label="Dirección",
                type=CorrectionFieldType.STRING,
                name=LegalRepresentativeField.ADDRESS.value,
                initial_value=self.address,
                options=None,
            ),
        ]
