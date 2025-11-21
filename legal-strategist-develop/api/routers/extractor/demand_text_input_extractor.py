from fastapi import File, Form, UploadFile

from models.api import error_response
from models.pydantic import MissingPaymentDocumentType, MissingPaymentFile
from services.v2.document.demand_text.input import (
    DemandTextInputExtractor,
    DemandTextInputExtractorInput,
    DemandTextInputExtractorOutput,
)
from . import router


@router.post("/demand-text-input/", response_model=DemandTextInputExtractorOutput)
async def demand_text_input_post(
    text: str = Form(..., description="Demand text input raw text", max_length=32768),
    file_types: list[MissingPaymentDocumentType] = Form([], description="File types", max_length=10),
    files: list[UploadFile] = File([], description="PDF files", max_length=10),
):
    """Handles the extraction of a demand text input from a string and PDF files."""
    document_files: list[MissingPaymentFile] = []
    for file, file_type in zip(files, file_types):
        if file.content_type != "application/pdf":
            return error_response("Invalid file type", 400)
        document_files.append(MissingPaymentFile(document_type=file_type, upload_file=file))

    try:
        demand_text_input_extractor = DemandTextInputExtractor(DemandTextInputExtractorInput(
            files=document_files,
            text=text,
        ))
        information = demand_text_input_extractor.extract()
    except Exception as e:
        return error_response(f"Could not extract information from input: {e}", 500)
    return information
