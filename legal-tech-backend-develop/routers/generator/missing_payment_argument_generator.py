import os
import shutil
import tempfile
from fastapi import File, Form, UploadFile

from models.api import error_response
from models.pydantic import MissingPaymentDocumentType
from services.v2.document.bill import (
    BillExtractor,
    BillExtractorInput,
)
from services.v2.document.demand_text.missing_payment_argument import (
    MissingPaymentArgumentGenerator,
    MissingPaymentArgumentGeneratorInput,
    MissingPaymentArgumentGeneratorOutput,
)
from services.v2.document.promissory_note import (
    PromissoryNoteExtractor,
    PromissoryNoteExtractorInput,
)
from . import router


@router.post("/missing-payment-argument/", response_model= MissingPaymentArgumentGeneratorOutput)
async def missing_payment_argument_post(
    reason: str = Form(..., description="Reason to argue about a missing payment", max_length=2048),
    document_type: MissingPaymentDocumentType = Form(..., description="Document type"),
    file: UploadFile = File(..., description="Document PDF file"),
):
    """Handles the generation of a missing payment argument given a PDF file."""
    if file.content_type != "application/pdf":
        return error_response("Invalid file type", 400)

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        try:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
            document = None
            match document_type:
                case MissingPaymentDocumentType.BILL:
                    extractor = BillExtractor(BillExtractorInput(file_path=temp_file_path))
                    document = extractor.extract()
                case MissingPaymentDocumentType.PROMISSORY_NOTE:
                    extractor = PromissoryNoteExtractor(PromissoryNoteExtractorInput(file_path=temp_file_path))
                    document = extractor.extract()
            generator = MissingPaymentArgumentGenerator(MissingPaymentArgumentGeneratorInput(
                document=document.structured_output,
                document_type=document_type,
                reason=reason,
            ))
            missing_payment_argument = generator.generate()
            if missing_payment_argument.metrics:
                missing_payment_argument.metrics.llm_invocations += document.metrics.llm_invocations
                missing_payment_argument.metrics.time += document.metrics.time
                missing_payment_argument.metrics.submetrics = [document.metrics]
        except Exception as e:
            return error_response(f"Could not generate argument from {document_type.value} document: {e}", 500)
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    return missing_payment_argument
