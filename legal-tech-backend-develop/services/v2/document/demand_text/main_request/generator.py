import time

from services.v2.document.base import BaseGenerator, Metrics
from .models import (
    DemandTextMainRequestGeneratorInput,
    DemandTextMainRequestGeneratorOutput,
    DemandTextMainRequestStructure,
)


class DemandTextMainRequestGenerator(BaseGenerator):
    """Demand text main request generator (deterministic, no LLM)."""

    def __init__(self, input: DemandTextMainRequestGeneratorInput) -> None:
        super().__init__()
        self.input = input

    def generate(self) -> DemandTextMainRequestGeneratorOutput:
        """Generate main request structure from input."""
        metrics = Metrics(label="DemandTextMainRequestGenerator.generate")
        start_time = time.time()

        content = self._create_content()
        structure = DemandTextMainRequestStructure(content=content)
        structure.normalize()

        metrics.time = round(time.time() - start_time, 4)
        return DemandTextMainRequestGeneratorOutput(
            metrics=metrics,
            structured_output=structure if structure is not None else None,
        )

    def _create_content(self) -> str:
        lines: list[str] = [
            (
                "POR TANTO, en mérito de lo expuesto, y de conformidad a lo prescrito "
                "en los Arts. 434 y siguientes del Código de Procedimiento Civil,"
            ),
        ]

        # Construcción segura de los demandados
        debtors_lines: list[str] = []

        for debtor in self.input.debtors or []:
            if not debtor.name:
                continue

            # Representación legal SOLO si viene en el pagaré
            debtor_representation = ""

            if debtor.legal_representatives:
                reps = [
                    rep.name
                    for rep in debtor.legal_representatives
                    if rep and rep.name
                ]
                if reps:
                    if len(reps) == 1:
                        debtor_representation = f", representada por {reps[0]}"
                    else:
                        debtor_representation = (
                            f", representada por {', '.join(reps[:-1])} y {reps[-1]}"
                        )

            debtors_lines.append(
                f"en contra de {debtor.name}{debtor_representation}, "
                f"en su calidad de deudor principal"
            )

        # Construcción de la línea principal
        if len(debtors_lines) == 1:
            current_line = (
                "RUEGO A US. tener por interpuesta la presente demanda ejecutiva "
                f"{debtors_lines[0]}"
            )
        elif len(debtors_lines) > 1:
            current_line = (
                "RUEGO A US. tener por interpuesta la presente demanda ejecutiva "
                f"{', '.join(debtors_lines[:-1])} y {debtors_lines[-1]}"
            )
        else:
            current_line = "RUEGO A US. tener por interpuesta la presente demanda ejecutiva"

        # Aval / co-deudor (NUNCA con representante legal)
        if self.input.co_debtors:
            co_debtors_names = [
                co_debtor.name
                for co_debtor in self.input.co_debtors
                if co_debtor.name
            ]
            if co_debtors_names:
                if len(co_debtors_names) == 1:
                    current_line += (
                        f", y en contra de {co_debtors_names[0]}, "
                        "en su calidad de aval, fiador y codeudor solidario"
                    )
                else:
                    current_line += (
                        f", y en contra de {', '.join(co_debtors_names[:-1])} "
                        f"y {co_debtors_names[-1]}, "
                        "en su calidad de avales, fiadores y codeudores solidarios"
                    )

        # Cierre de la petición
        current_line += (
            ", ordenando se despache mandamiento de ejecución y embargo en su contra "
            f"por la suma total de ${self.input.amount}.- "
            f"({self.input.amount}), más los intereses que correspondan, "
            "ordenando se siga adelante con esta ejecución hasta hacer a mi representado "
            "entero y cumplido pago de lo adeudado, con costas."
        )

        lines.append(current_line)

        return "\n\n".join(lines)
