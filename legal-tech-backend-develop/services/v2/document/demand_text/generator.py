import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from models.pydantic import DefendantType, Locale
from services.v2.document.base import BaseGenerator, Metrics
from util import int_to_ordinal
from .additional_request import (
    DemandTextAdditionalRequestGenerator,
    DemandTextAdditionalRequestGeneratorInput,
    DemandTextAdditionalRequestGeneratorOutput,
)
from .header import (
    DemandTextHeaderGenerator,
    DemandTextHeaderGeneratorInput,
)
from .main_request import (
    DemandTextMainRequestGenerator,
    DemandTextMainRequestGeneratorInput,
    DemandTextMainRequestGeneratorOutput,
)
from .missing_payment_argument import (
    MissingPaymentArgumentGenerator,
    MissingPaymentArgumentGeneratorInput,
    MissingPaymentArgumentGeneratorOutput,
    MissingPaymentArgumentStructure,
)
from .opening import (
    DemandTextOpeningGenerator,
    DemandTextOpeningGeneratorInput,
    DemandTextOpeningGeneratorOutput,
)
from .summary import (
    DemandTextSummaryGenerator,
    DemandTextSummaryGeneratorInput,
)
from .models import DemandTextGeneratorInput, DemandTextGeneratorOutput, DemandTextStructure


class DemandTextGenerator(BaseGenerator):
    """Demand text generator."""
    
    def __init__(self, input: DemandTextGeneratorInput) -> None:
        super().__init__()
        self.input = input

    def generate(self) -> DemandTextGeneratorOutput:
        """Generates structured output from input."""
        metrics = Metrics(label=f"DemandTextGenerator.generate", submetrics=[])
        start_time = time.time()

        structure = DemandTextStructure(
            court=f"S.J.L CIVIL DE {self.input.city.upper()}" if self.input.city else None,
        )

        demand_text_header_generator = DemandTextHeaderGenerator(DemandTextHeaderGeneratorInput(
            defendants=self.input.defendants,
            legal_subject=self.input.legal_subject,
            plaintiffs=[self.input.plaintiff],
            sponsoring_attorneys=self.input.sponsoring_attorneys,
        ))
        try:
            header_structure = demand_text_header_generator.generate()
            if sub_metrics := header_structure.metrics:
                metrics.submetrics.append(sub_metrics)
                metrics.llm_invocations += sub_metrics.llm_invocations
            if output := header_structure.structured_output:
                structure.header = output.content
        except Exception as e:
            logging.warning(f"Could not generate demand text header: {e}")
        
        demand_text_summary_generator = DemandTextSummaryGenerator(DemandTextSummaryGeneratorInput(
            secondary_requests=self.input.secondary_requests,
        ))
        try:
            summary_structure = demand_text_summary_generator.generate()
            if sub_metrics := summary_structure.metrics:
                metrics.submetrics.append(sub_metrics)
                metrics.llm_invocations += sub_metrics.llm_invocations
            if output := summary_structure.structured_output:
                structure.summary = output.content
        except Exception as e:
            logging.warning(f"Could not generate demand text summary: {e}")
        
        demand_text_opening_generator = DemandTextOpeningGenerator(DemandTextOpeningGeneratorInput(
            co_debtors=[defendant for defendant in self.input.defendants or [] if defendant.type == DefendantType.CO_DEBTOR],
            creditor=self.input.plaintiff,
            debtors=[defendant for defendant in self.input.defendants or [] if defendant.type == DefendantType.DEBTOR],
            document_count=len(self.input.documents or []),
            legal_representatives=self.input.legal_representatives,
            sponsoring_attorneys=self.input.sponsoring_attorneys,
        ))

        argument_requests_generators: list[MissingPaymentArgumentGenerator] = []
        for document, document_type, reason in zip(self.input.documents or [], self.input.document_types or [], self.input.reasons_per_document or []):
            argument_requests_generators.append(MissingPaymentArgumentGenerator(
                MissingPaymentArgumentGeneratorInput(
                    document=document,
                    document_type=document_type,
                    over_creditor=self.input.plaintiff,
                    structured_reason=reason,
                )
            ))

        demand_text_main_request_generator = DemandTextMainRequestGenerator(DemandTextMainRequestGeneratorInput(
            amount=self.input.amount,
            amount_currency=self.input.amount_currency,
            co_debtors=[defendant for defendant in self.input.defendants or [] if defendant.type == DefendantType.CO_DEBTOR],
            debtors=[defendant for defendant in self.input.defendants or [] if defendant.type == DefendantType.DEBTOR],
        ))

        additional_request_generators: list[DemandTextAdditionalRequestGenerator] = []
        for additional_request in self.input.secondary_requests or []:
            additional_request_generators.append(DemandTextAdditionalRequestGenerator(
                DemandTextAdditionalRequestGeneratorInput(
                    context=additional_request.context,
                    creditor=self.input.plaintiff,
                    document_types=self.input.document_types,
                    nature=additional_request.nature,
                    sponsoring_attorneys=self.input.sponsoring_attorneys,
                )
            ))

        # Execute AI generators in parallel.
        with ThreadPoolExecutor() as executor:
            futures = {}

            futures[executor.submit(demand_text_opening_generator.generate)] = "opening"
            futures[executor.submit(demand_text_main_request_generator.generate)] = "main_request"

            argument_futures = {
                executor.submit(gen.generate): ("argument_requests", idx)
                for idx, gen in enumerate(argument_requests_generators)
            }
            additional_futures = {
                executor.submit(gen.generate): ("additional_requests", idx)
                for idx, gen in enumerate(additional_request_generators)
            }

            futures.update(argument_futures)
            futures.update(additional_futures)

            argument_results: list[MissingPaymentArgumentGeneratorOutput | None] = [None] * len(argument_requests_generators)
            additional_results: list[DemandTextAdditionalRequestGeneratorOutput | None] = [None] * len(additional_request_generators)

            for future in as_completed(futures):
                category = futures[future]

                try:
                    result = future.result()
                except Exception as e:
                    logging.warning(f"Could not generate {category}: {e}")
                    result = []

                if category == "opening":
                    opening_structure: DemandTextOpeningGeneratorOutput = result
                    if sub_metrics := opening_structure.metrics:
                        metrics.submetrics.append(sub_metrics)
                        metrics.llm_invocations += sub_metrics.llm_invocations
                    if output := opening_structure.structured_output:
                        structure.opening = output.content

                elif category == "main_request":
                    main_request_structure: DemandTextMainRequestGeneratorOutput = result
                    if sub_metrics := main_request_structure.metrics:
                        metrics.submetrics.append(sub_metrics)
                        metrics.llm_invocations += sub_metrics.llm_invocations
                    if output := main_request_structure.structured_output:
                        structure.main_request = output.content

                elif isinstance(category, tuple):
                    list_name, idx = category
                    if list_name == "argument_requests":
                        argument_results[idx] = result
                    elif list_name == "additional_requests":
                        additional_results[idx] = result
        
        # Add missing payment arguments.
        if argument_results:
            structure.missing_payment_arguments = []
        for idx, argument in enumerate(list(filter(None, argument_results))):
            if sub_metrics := argument.metrics:
                metrics.submetrics.append(sub_metrics)
                metrics.llm_invocations += sub_metrics.llm_invocations
            if output := argument.structured_output:
                structure.missing_payment_arguments.append(
                    MissingPaymentArgumentStructure(argument=f"{idx + 1}) {output.argument}", document_type=output.document_type)
                )
        
        # Add additional requests.
        additional_requests: list[str | None] = []
        for additional_request in list(filter(None, additional_results)):
            if sub_metrics := additional_request.metrics:
                metrics.submetrics.append(sub_metrics)
                metrics.llm_invocations += sub_metrics.llm_invocations
            if output := additional_request.structured_output:
                additional_requests.append(output.content)
        if additional_requests:
            enumerated_requests = [f"{int_to_ordinal(idx + 1, Locale.ES_ES)} OTROSÍ: {request}" for idx, request in enumerate(list(filter(None, additional_requests)))]
            structure.additional_requests = "\n\n".join(enumerated_requests)

        metrics.time = round(time.time() - start_time, 4)
        return DemandTextGeneratorOutput(metrics=metrics, structured_output=structure)
