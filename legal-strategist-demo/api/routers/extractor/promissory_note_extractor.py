import os
import shutil
import tempfile
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import JSONResponse

from models.pydantic import ErrorResponse, PromissoryNote
from services.extractor import PromissoryNoteExtractor
from routers.base import get_api_key


router = APIRouter()


@router.post("/promissory_note_by_file/", response_model=PromissoryNote, dependencies=[Depends(get_api_key)])
async def promissory_note_by_file_extractor(
    context: Optional[str] = Form(None, description="Additional context to consider", max_length=512),
    file: UploadFile = File(..., description="Promissory note PDF file"),
):
    if file.content_type != "application/pdf":
        error_response = ErrorResponse(error="Invalid file type", code=400)
        return JSONResponse(status_code=400, content=error_response.model_dump())

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        try:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
            extractor = PromissoryNoteExtractor(context)
            promissory_note = extractor.extract_from_file_path(temp_file_path)
        except Exception as e:
            error_response = ErrorResponse(error=f"Internal error: {e}", code=500)
            return JSONResponse(status_code=500, content=error_response.model_dump())
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    if promissory_note is None:
        error_response = ErrorResponse(error="Could not extract attributes from promissory note", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    return promissory_note
