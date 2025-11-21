from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import JSONResponse

from models.api import DemandTextGenerationResponse, ErrorResponse
from models.pydantic import MissingPaymentDocumentType, MissingPaymentFile
from services.extractor import DemandTextInputExtractor
from services.generator import JudicialCollectionDemandTextGenerator
from routers.base import get_api_key


router = APIRouter()


@router.post("/chat/", response_model=DemandTextGenerationResponse, dependencies=[Depends(get_api_key)])
async def chat(
    content: str = Form(..., description="Chat content"),
    seed: int = Form(0, description="Random generation seed for the IA"),
    files: list[UploadFile] = File([], description="PDF files", max_length=10),
    file_types: list[MissingPaymentDocumentType] = File([], description="File types", max_length=10),
):
    document_files = []
    for file, file_type in zip(files, file_types):
        if file.content_type != "application/pdf":
            error_response = ErrorResponse(error="Invalid promissory note file type", code=400)
            return JSONResponse(status_code=400, content=error_response.model_dump())
        document_files.append(MissingPaymentFile(document_type=file_type, upload_file=file))

    try:
        demand_text_input_extractor = DemandTextInputExtractor()
        demand_text_input = demand_text_input_extractor.extract_from_text(content)
    except Exception as e:
        error_response = ErrorResponse(error=f"Internal error (input extraction): {e}", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    try:
        generator = JudicialCollectionDemandTextGenerator(demand_text_input, seed)
        demand_text = generator.generate_from_files(document_files, True)
    except Exception as e:
        error_response = ErrorResponse(error=f"Internal error (demand text generation): {e}", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    
    if demand_text is None:
        error_response = ErrorResponse(error="Could not generate demand text", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    return demand_text
