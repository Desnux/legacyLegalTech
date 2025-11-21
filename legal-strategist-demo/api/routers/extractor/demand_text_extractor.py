import os
import shutil
import tempfile

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import JSONResponse

from models.pydantic import DemandText, ErrorResponse, JudicialCollectionDemandTextInput
from services.extractor import DemandTextExtractor
from routers.base import get_api_key


router = APIRouter()


@router.post("/demand_text_by_file/", response_model=JudicialCollectionDemandTextInput, dependencies=[Depends(get_api_key)])
async def demand_text_by_file_extractor(
    file: UploadFile = File(..., description="Demand text PDF file"),
):
    if file.content_type != "application/pdf":
        error_response = ErrorResponse(error="Invalid file type", code=400)
        return JSONResponse(status_code=400, content=error_response.model_dump())

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        try:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
            extractor = DemandTextExtractor()
            demand_text_input = extractor.extract_from_file_path(temp_file_path)
        except Exception as e:
            error_response = ErrorResponse(error=f"Internal error: {e}", code=500)
            return JSONResponse(status_code=500, content=error_response.model_dump())
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    if demand_text_input is None:
        error_response = ErrorResponse(error="Could not extract input attributes from demand text", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    return demand_text_input


@router.post("/demand_text_by_text/", response_model=DemandText, dependencies=[Depends(get_api_key)])
async def demand_text_by_text_extractor(
    context: str | None = Form(None, description="Additional context to consider", max_length=512),
    text: str = Form(..., description="Demand text raw text", max_length=32768),
):
    try:
        extractor = DemandTextExtractor(context)
        demand_text = extractor.extract_from_text(text)
    except Exception as e:
        error_response = ErrorResponse(error=f"Internal error: {e}", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())

    if demand_text is None:
        error_response = ErrorResponse(error="Could not extract attributes from demand_text", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    return demand_text
