from fastapi import APIRouter, Body, Depends, File, Form, UploadFile
from fastapi.responses import JSONResponse

from config import Config
from models.api import DemandTextGenerationResponse
from models.pydantic import ErrorResponse, JudicialCollectionDemandText, JudicialCollectionDemandTextInput, MissingPaymentDocumentType, MissingPaymentFile
from services.generator import JudicialCollectionDemandTextGenerator
from routers.base import get_api_key


router = APIRouter()


@router.post("/judicial_collection_demand_text_by_file/", response_model=JudicialCollectionDemandText, dependencies=[Depends(get_api_key)])
async def judicial_collection_demand_text_by_file_generator(
    input: JudicialCollectionDemandTextInput = Body(..., description="Required information"),
    seed: int = Form(0, description="Random generation seed for the IA"),
    files: list[UploadFile] = File([], description="PDF files", max_length=10),
    file_types: list[MissingPaymentDocumentType] = File([], description="File types", max_length=10),
):
    document_files = []
    total_file_size = 0
    for file, file_type in zip(files, file_types):
        if file.content_type != "application/pdf":
            error_response = ErrorResponse(error="Invalid promissory note file type", code=400)
            return JSONResponse(status_code=400, content=error_response.model_dump())
        
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        if file_size > Config.MAX_FILE_SIZE_BYTES:
            error_response = ErrorResponse(error=f"File '{file.filename}' exceeds the maximum allowed size of {Config.MAX_FILE_SIZE_MB}MB.", code=413)
            return JSONResponse(status_code=413, content=error_response.model_dump())
        
        total_file_size += file_size
        if total_file_size > Config.MAX_BATCH_FILE_SIZE_BYTES:
            error_response = ErrorResponse(error=f"Total uploaded files exceed the maximum batch size of {Config.MAX_BATCH_FILE_SIZE_MB}MB.", code=413)
            return JSONResponse(status_code=413, content=error_response.model_dump())

        document_files.append(MissingPaymentFile(document_type=file_type, upload_file=file))

    try:
        generator = JudicialCollectionDemandTextGenerator(input, seed)
        demand_text = generator.generate_from_files(document_files)
    except Exception as e:
        error_response = ErrorResponse(error=f"Internal error: {e}", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    
    if demand_text is None:
        error_response = ErrorResponse(error="Could not generate demand text", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    return JudicialCollectionDemandText(text=demand_text.raw_text)


@router.post("/judicial_collection_demand_text_structure_by_file/", response_model=DemandTextGenerationResponse, dependencies=[Depends(get_api_key)])
async def judicial_collection_demand_text_structure_by_file_generator(
    input: JudicialCollectionDemandTextInput = Body(..., description="Required information"),
    seed: int = Form(0, description="Random generation seed for the IA"),
    files: list[UploadFile] = File([], description="PDF files", max_length=10),
    file_types: list[MissingPaymentDocumentType] = File([], description="File types", max_length=10),
):
    document_files = []
    total_file_size = 0
    for file, file_type in zip(files, file_types):
        if file.content_type != "application/pdf":
            error_response = ErrorResponse(error="Invalid promissory note file type", code=400)
            return JSONResponse(status_code=400, content=error_response.model_dump())
        
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        if file_size > Config.MAX_FILE_SIZE_BYTES:
            error_response = ErrorResponse(error=f"File '{file.filename}' exceeds the maximum allowed size of {Config.MAX_FILE_SIZE_MB}MB.", code=413)
            return JSONResponse(status_code=413, content=error_response.model_dump())
        
        total_file_size += file_size
        if total_file_size > Config.MAX_BATCH_FILE_SIZE_BYTES:
            error_response = ErrorResponse(error=f"Total uploaded files exceed the maximum batch size of {Config.MAX_BATCH_FILE_SIZE_MB}MB.", code=413)
            return JSONResponse(status_code=413, content=error_response.model_dump())

        document_files.append(MissingPaymentFile(document_type=file_type, upload_file=file))

    try:
        generator = JudicialCollectionDemandTextGenerator(input, seed)
        demand_text = generator.generate_from_files(document_files, True)
    except Exception as e:
        error_response = ErrorResponse(error=f"Internal error: {e}", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    
    if demand_text is None:
        error_response = ErrorResponse(error="Could not generate demand text", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    return demand_text
