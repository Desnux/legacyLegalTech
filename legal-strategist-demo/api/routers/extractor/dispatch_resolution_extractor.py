import os
import shutil
import tempfile

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import JSONResponse

from models.pydantic import DispatchResolutionStructure, ErrorResponse
from services.extractor import DispatchResolutionExtractor
from routers.base import get_api_key


router = APIRouter()


@router.post("/dispatch_resolution_by_file/", response_model=DispatchResolutionStructure, dependencies=[Depends(get_api_key)])
async def dispatch_resolution_by_file_extractor(
    file: UploadFile = File(..., description="Dispatch resolution PDF file"),
):
    if file.content_type != "application/pdf":
        error_response = ErrorResponse(error="Invalid file type", code=400)
        return JSONResponse(status_code=400, content=error_response.model_dump())

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        try:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
            extractor = DispatchResolutionExtractor()
            structure = extractor.extract_from_file_path(temp_file_path)
        except Exception as e:
            error_response = ErrorResponse(error=f"Internal error: {e}", code=500)
            return JSONResponse(status_code=500, content=error_response.model_dump())
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    if structure is None:
        error_response = ErrorResponse(error="Could not extract structure from dispatch resolution", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    return structure
