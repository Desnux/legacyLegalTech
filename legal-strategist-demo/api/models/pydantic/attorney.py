from enum import Enum

from pydantic import BaseModel, Field

from .correction import CorrectionField, CorrectionFieldType


class AttorneyField(str, Enum):
    NAME = "name"
    IDENTIFIER = "identifier"
    ADDRESS = "address"


class Attorney(BaseModel):
    name: str | None = Field(None, description="Name of the attorney")
    identifier: str | None = Field(None, description="RUT or C.I.Nº of the attorney in the format XX.XXX.XXX-X or X.XXX.XXX-X")
    address: str | None = Field(None, description="Address of the attorney")

    def normalize(self) -> None:
        if self.identifier:
            if len(self.identifier) > 2:
                self.identifier = self.identifier[:-2].replace("-", ".") + "-" + self.identifier[-2 + 1:].lower()

    def get_correction_fields(self) -> list[CorrectionField]:
        return [
            CorrectionField(
                label="Nombre",
                type=CorrectionFieldType.STRING,
                name=AttorneyField.NAME.value,
                initial_value=self.name,
                options=None,
            ),
            CorrectionField(
                label="Identificador",
                type=CorrectionFieldType.STRING,
                name=AttorneyField.IDENTIFIER.value,
                initial_value=self.identifier,
                options=None,
            ),
            CorrectionField(
                label="Dirección",
                type=CorrectionFieldType.STRING,
                name=AttorneyField.ADDRESS.value,
                initial_value=self.address,
                options=None,
            ),
        ]