from enum import Enum
from pydantic import BaseModel, Field

from .legal_representative import LegalRepresentative

def _is_legal_entity_name(name: str | None) -> bool:
    if not name:
        return False
    t = name.lower()
    markers = (
        "spa", "sp.a", "s.a", "ltda", "eirl", "limitada",
        "sociedad", "inversiones", "inmobiliaria", "comercial",
        "agrícola", "servicios",
    )
    return any(m in t for m in markers)



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
        # 1) Decide tipo de entidad por el NOMBRE (más confiable que el umbral del RUT)
        self.entity_type = (
            DefendantEntityType.LEGAL
            if _is_legal_entity_name(self.name)
            else DefendantEntityType.NATURAL
        )

        # 2) Normaliza identificador si existe (sin depender del umbral para decidir entidad)
        if self.identifier and len(self.identifier) > 2:
            try:
                self.identifier = (
                    self.identifier[:-2].replace("-", ".")
                    + "-"
                    + self.identifier[-1:].lower()
                )
            except Exception:
                # si viene malformateado, no rompemos el flujo
                pass

        # 3) Regla de negocio: persona natural NO tiene representante legal
        if self.entity_type == DefendantEntityType.NATURAL:
            self.legal_representatives = None

        # 4) Si quedó como persona jurídica, normaliza reps si existen
        if self.legal_representatives:
            for rep in self.legal_representatives:
                rep.normalize()

