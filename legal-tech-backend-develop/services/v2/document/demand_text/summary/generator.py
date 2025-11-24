import logging
import time

from models.pydantic import JudicialCollectionLegalRequest, Locale
from services.v2.document.base import BaseGenerator, Metrics, Response
from util import int_to_ordinal
from .models import (
    DemandTextSummaryGeneratorInput,
    DemandTextSummaryGeneratorOutput,
    DemandTextSummaryStructure,
)


class DemandTextSummaryGenerator(BaseGenerator):
    """Demant text summary generator."""

    def __init__(self, input: DemandTextSummaryGeneratorInput) -> None:
        super().__init__()
        self.input = input
        self.generator = self._create_structured_generator(Response)
    
    def generate(self) -> DemandTextSummaryGeneratorOutput:
        """Generate demand text summary structure from input."""
        metrics = Metrics(label="DemandTextSummaryGenerator.generate")
        start_time = time.time()

        lines: list[str] = []
        for idx, secondary_request in enumerate(self.input.secondary_requests or []):
            match = next((item for item in self.input.custom_summaries or [] if item[0] == idx), None)
            if match:
                lines.append(match[1])
            elif secondary_request.nature == JudicialCollectionLegalRequest.OTHER and secondary_request.context:
                prompt = f"""
                Generate a brief and formal legal sentence in es_ES that summarizes a request or obligation using an impersonal tone in less than 8 words.
                For context of the request or obligation, consider: <context>{secondary_request.context}</context>
                For an example of output (do not copy), consider: <example>SEÑALA BIENES PARA LA TRABA DEL EMBARGO</example>
                """
                try:
                    request: Response = self.generator.invoke(prompt)
                    metrics.llm_invocations += 1
                    if output := request.output:
                        lines.append(output.upper().strip())
                except Exception as e:
                    logging.warning(f"Could not generate additional request summary: {e}")
                    continue
            elif secondary_request.nature == JudicialCollectionLegalRequest.OTHER:
                continue
            else:
                lines.append(secondary_request.nature.to_localized_string(Locale.ES_ES))

        formatted_lines = [f"{int_to_ordinal(i + 1, Locale.ES_ES)} OTROSÍ: {segment}" for i, segment in enumerate(lines)]
        formatted_lines.insert(0, "EN LO PRINCIPAL: DEMANDA EJECUTIVA Y SOLICITA SE DESPACHE MANDAMIENTO DE EJECUCIÓN Y EMBARGO")
        structure = DemandTextSummaryStructure(content="; ".join(formatted_lines))
        structure.normalize()

        metrics.time = round(time.time() - start_time, 4)
        return DemandTextSummaryGeneratorOutput(
            metrics=metrics,
            structured_output=structure if structure is not None else None,
            structured_summaries=[(idx, line) for idx, line in enumerate(lines)],
        )
