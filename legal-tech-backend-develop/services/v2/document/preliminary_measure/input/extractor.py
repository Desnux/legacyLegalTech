import logging
import os
import shutil
import tempfile
import time
from fastapi import UploadFile

from services.v2.document.base import BaseExtractor, Metrics
from services.v2.document.coopeuch_report import (
    CoopeuchReportExtractor,
    CoopeuchReportExtractorInput,
    CoopeuchReportExtractorOutput,
)
from .models import (
    MeasureInformation,
    PreliminaryMeasureInputExtractorInput,
    PreliminaryMeasureInputExtractorOutput,
    PreliminaryMeasureInputInformation,
)


class PreliminaryMeasureInputExtractor(BaseExtractor):
    """Preliminary measure input extractor."""

    def __init__(self, input: PreliminaryMeasureInputExtractorInput) -> None:
        super().__init__()
        self.input = input

    def extract(self) -> PreliminaryMeasureInputExtractorOutput:
        """Extract structured information from input."""
        information = PreliminaryMeasureInputInformation(
            measure_information=MeasureInformation(
                local_police_number=self.input.local_police_number,
                communication_date=self.input.communication_date,
                coopeuch_registry_uri=self.input.coopeuch_registry_uri,
                transaction_to_self_uri=self.input.transaction_to_self_uri,
                payment_to_account_uri=self.input.payment_to_account_uri,
                user_report_uri=self.input.user_report_uri,
                safesigner_report_uri=self.input.safesigner_report_uri,
                mastercard_connect_report_uri=self.input.mastercard_connect_report_uri,
                celmedia_report_uri=self.input.celmedia_report_uri,
            )
        )
        metrics = Metrics(label=f"PreliminaryMeasureInputExtractor.extract", submetrics=[])
        start_time = time.time()

        document = self._extract_document()
        if document_metrics := document.metrics:
            metrics.llm_invocations += document_metrics.llm_invocations
            metrics.submetrics.append(document_metrics)
        if document_output := document.structured_output:
            information.city = document_output.city
            information.total_transaction_amount = document_output.total_transaction_amount
            information.currency_type = document_output.currency_type
            information.claimed_transactions = document_output.claimed_transactions
            information.claimant_partner = document_output.claimant_partner
            information.claimant_request = document_output.claimant_request

        information.normalize()

        metrics.time = round(time.time() - start_time, 4)
        return PreliminaryMeasureInputExtractorOutput(metrics=metrics, structured_output=information)

    def _extract_document(self) -> CoopeuchReportExtractorOutput | None:
        if not self.input.file:
            return None
        document = self._process_file(self.input.file)
        return document

    def _process_file(self, file: UploadFile) -> CoopeuchReportExtractorOutput | None:
        temp_file_path = None
        document: CoopeuchReportExtractorOutput | None = None
        try:
            file.file.seek(0)
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                shutil.copyfileobj(file.file, temp_file)
                temp_file_path = temp_file.name
            extractor = CoopeuchReportExtractor(CoopeuchReportExtractorInput(file_path=temp_file_path))
            document = extractor.extract()
        except Exception as e:
            logging.warning(f"Error processing document {file.filename} ({type(e).__name__}): {e}")
            return None
        finally:
            if temp_file_path is not None and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
        return document
