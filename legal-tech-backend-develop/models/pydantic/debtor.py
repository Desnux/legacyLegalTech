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



class Debtor(BaseModel):
    name: str | None = Field(None, description="Name of the debtor or suscriptor")
    identifier: str | None = Field(None, description="RUT or C.I.Nº of the debtor or suscriptor in the format XX.XXX.XXX-X or X.XXX.XXX-X")
    occupation: str | None = Field(None, description="Occupation or profession of the debtor")
    address: str | None = Field(None, description="Address of debtor or suscriptor")
    legal_representatives: list[LegalRepresentative] | None = Field(None, description="Legal representatives of the debtor or suscriptor")

    def normalize(self) -> None:
        # 1) Normaliza identificador si existe (sin usar umbral para decidir reps)
        if self.identifier and len(self.identifier) > 2:
            try:
                self.identifier = (
                    self.identifier[:-2].replace("-", ".")
                    + "-"
                    + self.identifier[-1:].lower()
                )
            except Exception:
                pass

        # 2) Regla: solo persona jurídica puede tener representante legal
        if not _is_legal_entity_name(self.name):
            self.legal_representatives = None

        # 3) Si quedan reps, normalizarlos
        if self.legal_representatives:
            for rep in self.legal_representatives:
                rep.normalize()

