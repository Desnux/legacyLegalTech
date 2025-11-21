from enum import Enum

from pydantic import BaseModel, Field

from .correction import CorrectionField, CorrectionFieldType


class PlaintiffField(str, Enum):
    NAME = "name"
    IDENTIFIER = "identifier"


class Plaintiff(BaseModel):
    name: str | None = Field(None, description="Name of the plaintiff")
    identifier: str | None = Field(None, description="RUT or C.I.Nº of the plaintiff in the format XX.XXX.XXX-X or X.XXX.XXX-X")

    def normalize(self) -> None:
        if self.identifier:
            if len(self.identifier) > 2:
                self.identifier = self.identifier[:-2].replace("-", ".") + "-" + self.identifier[-2 + 1:].lower()

    def get_correction_fields(self) -> list[CorrectionField]:
        return [
            CorrectionField(
                label="Nombre",
                type=CorrectionFieldType.STRING,
                name=PlaintiffField.NAME.value,
                initial_value=self.name,
                options=None,
            ),
            CorrectionField(
                label="Identificador",
                type=CorrectionFieldType.STRING,
                name=PlaintiffField.IDENTIFIER.value,
                initial_value=self.identifier,
                options=None,
            ),
        ]
