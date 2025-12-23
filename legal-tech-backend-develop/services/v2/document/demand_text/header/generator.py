import time

from models.pydantic import Attorney, Creditor, Defendant, LegalRepresentative, LegalSubject, Litigant, Plaintiff
from models.pydantic.defendant import DefendantEntityType
from services.v2.document.base import BaseGenerator, Metrics
from util import int_to_roman
from .models import (
    DemandTextHeaderGeneratorInput,
    DemandTextHeaderGeneratorOutput,
    DemandTextHeaderStructure,
)


class DemandTextHeaderGenerator(BaseGenerator):
    """Demant text header generator."""

    def __init__(self, input: DemandTextHeaderGeneratorInput) -> None:
        super().__init__()
        self.input = input
    
    def generate(self) -> DemandTextHeaderGeneratorOutput:
        """Generate demand text header structure from input."""
        metrics = Metrics(label="DemandTextHeaderGenerator.generate")
        start_time = time.time()

        lines = ["PROCEDIMIENTO : EJECUTIVO"]
        lines.append({
            LegalSubject.BILL_COLLECTION: "MATERIA : COBRO DE FACTURA",
            LegalSubject.GENERAL_COLLECTION: "MATERIA : CUMPLIMIENTO OBLIGACIÓN DE DAR",
            LegalSubject.PROMISSORY_NOTE_COLLECTION: "MATERIA : COBRO DE PAGARÉ"
        }.get(self.input.legal_subject, "MATERIA : CUMPLIMIENTO OBLIGACIÓN DE DAR"))

        lines.extend(self._process_entities("DEMANDANTE", self.input.plaintiffs or []))
        lines.extend(self._process_entities("ABOGADO PATROCINANTE", self.input.sponsoring_attorneys or []))
        lines.extend(self._process_defendants())

        structure = DemandTextHeaderStructure(content="\n".join(lines))
        structure.normalize()

        metrics.time = round(time.time() - start_time, 4)
        return DemandTextHeaderGeneratorOutput(metrics=metrics, structured_output=structure if structure is not None else None)
    
    def _process_entities(self, 
        label: str,
        entities: list[Attorney | Creditor | Defendant | LegalRepresentative | Litigant | Plaintiff],
        start_idx: int | None = None,
    ) -> list[str]:
        """Helper method to process plaintiffs, defendants, and representatives."""
        lines = []
        if not entities:
            return lines

        multiple = len(entities) > 1
        if start_idx is None:
            start_idx = 1
        else:
            multiple = True
        for idx, entity in enumerate(entities, start=start_idx):
            if entity.name:
                label = f"{label} {int_to_roman(idx)}" if multiple else label
                lines.append(f"{label} : {entity.name.upper()}")
                if entity.identifier:
                    lines.append(f"RUT : {entity.identifier.upper()}")
            if entity.address:
                lines.append(f"DOMICILIO : {entity.address.upper()}")
        return lines

    def _process_defendants(self) -> list[str]:
        lines: list[str] = []
        start_idx = 1

        for defendant in self.input.defendants or []:
            lines.extend(self._process_entities("EJECUTADO", [defendant], start_idx))

            # 🔒 NORMALIZACIÓN CLAVE (AQUÍ VA)
            entity_type = defendant.entity_type
            if isinstance(entity_type, str):
                entity_type = entity_type.lower()

            print(
                "DEBUG DEFENDANT:",
                defendant.name,
                entity_type,
                type(defendant.entity_type),
                defendant.legal_representatives
            )


            # ❌ Persona natural: NUNCA representante
            if entity_type == "natural":
                start_idx += 1
                continue

            # ✅ Persona jurídica con representante explícito
            if entity_type == "legal" and defendant.legal_representatives:
                lines.extend(
                    self._process_entities(
                        "REPRESENTANTE",
                        defendant.legal_representatives
                    )
                )

            start_idx += 1

        return lines

