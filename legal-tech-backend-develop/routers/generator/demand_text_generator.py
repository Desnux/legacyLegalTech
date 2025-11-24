import logging
from fastapi import Body, File, Form, UploadFile

from config import Config
from models.api import error_response
from models.pydantic import MissingPaymentDocumentType, MissingPaymentFile
from services.v2.document.demand_text import (
    DemandTextGenerator,
    DemandTextGeneratorInput,
    DemandTextGeneratorOutput,
)
from services.v2.document.demand_text.input import (
    DemandTextInputExtractor,
    DemandTextInputExtractorInput,
)
from . import router


@router.post("/demand-text-from-raw-text/", response_model=DemandTextGeneratorOutput)
async def demand_text_from_raw_text_post(
    text: str = Form(..., description="Demand text input as raw text", max_length=32768),
    file_types: list[MissingPaymentDocumentType] = Form([], description="File types", max_length=10),
    files: list[UploadFile] = File([], description="PDF files", max_length=10),
):
    """Handles the generation of a demand text from raw text."""
    document_files: list[MissingPaymentFile] = []
    total_file_size = 0
    for file, file_type in zip(files, file_types):
        if file.content_type != "application/pdf":
            return error_response("Invalid promissory note file type", 400)
        
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        if file_size > Config.MAX_FILE_SIZE_BYTES:
            return error_response(f"File '{file.filename}' exceeds the maximum allowed size of {Config.MAX_FILE_SIZE_MB} MB.", 413)
        
        total_file_size += file_size
        if total_file_size > Config.MAX_BATCH_FILE_SIZE_BYTES:
            return error_response(f"Total uploaded files exceed the maximum batch size of {Config.MAX_BATCH_FILE_SIZE_MB} MB.", 413)

        document_files.append(MissingPaymentFile(document_type=file_type, upload_file=file))

    try:
        demand_text_input_extractor = DemandTextInputExtractor(DemandTextInputExtractorInput(
            files=document_files,
            text=text,
        ))
        information = demand_text_input_extractor.extract()
        logging.info(f"Demand text input extractor metrics: {information.metrics.model_dump_json()}")
    except Exception as e:
        return error_response(f"Could not extract information from input: {e}", 500, True)
    if not information.structured_output:
        return error_response(f"Could not extract information from input", 500)
    
    try:
        demand_text_generator = DemandTextGenerator(DemandTextGeneratorInput(
            **information.structured_output.model_dump(),
        ))
        structure = demand_text_generator.generate()
    except Exception as e:
        return error_response(f"Could not generate demand text: {e}", 500, True)
    return structure


@router.post("/demand-text-from-structure/", response_model=DemandTextGeneratorOutput)
async def demand_text_from_structure_post(
    input: DemandTextGeneratorInput = Body(..., description="Demand text input as structured json"),
):
    """Handles the generation of a demand text from structured input."""
    try:
        demand_text_generator = DemandTextGenerator(input)
        structure = demand_text_generator.generate()
    except Exception as e:
        return error_response(f"Could not generate demand text: {e}", 500, True)
    return structure
