from enum import Enum

from pydantic import BaseModel, Field

from .correction import CorrectionField, CorrectionFieldList, CorrectionFieldType
from .legal_representative import LegalRepresentative


class DefendantField(str, Enum):
    NAME = "name"
    IDENTIFIER = "identifier"
    OCCUPATION = "occupation"
    ADDRESS = "address"
    LEGAL_REPRESENTATIVES = "legal_representatives"


class DefendantType(str, Enum):
    DEBTOR = "debtor"
    CO_DEBTOR = "co_debtor"


class Defendant(BaseModel):
    name: str | None = Field(None, description="Name of the defendant")
    identifier: str | None = Field(None, description="RUT or C.I.Nº of the defendant in the format XX.XXX.XXX-X or X.XXX.XXX-X")
    occupation: str | None = Field(None, description="Occupation or profession of the defendant")
    address: str | None = Field(None, description="Address of the legal defendant")
    legal_representatives: list[LegalRepresentative] | None = Field(None, description="Legal representatives of the defendant")
    type: DefendantType | None = Field(None, description="Type of defendant, either 'debtor' or 'co_debtor'")

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
        if self.legal_representatives:
            for rep in self.legal_representatives:
                rep.normalize()

    def get_correction_fields(self) -> list[CorrectionField | CorrectionFieldList]:
        correction_fields = [
            CorrectionField(
                label="Nombre",
                type=CorrectionFieldType.STRING,
                name=DefendantField.NAME.value,
                initial_value=self.name,
                options=None,
            ),
            CorrectionField(
                label="Identificador",
                type=CorrectionFieldType.STRING,
                name=DefendantField.IDENTIFIER.value,
                initial_value=self.identifier,
                options=None,
            ),
            CorrectionField(
                label="Ocupación",
                type=CorrectionFieldType.STRING,
                name=DefendantField.OCCUPATION.value,
                initial_value=self.occupation,
                options=None,
            ),
            CorrectionField(
                label="Dirección",
                type=CorrectionFieldType.STRING,
                name=DefendantField.ADDRESS.value,
                initial_value=self.address,
                options=None,
            ),
        ]
        for index, legal_representative in enumerate(self.legal_representatives or []):
            correction_fields.append(CorrectionFieldList(
                label=f"Representante legal {index + 1}",
                name=f"{DefendantField.LEGAL_REPRESENTATIVES.value}.{index}",
                initial_value=legal_representative.get_correction_fields(),
            ))
        return correction_fields
