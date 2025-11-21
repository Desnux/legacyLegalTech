import os
import shutil
import tempfile
from fastapi import File, UploadFile

from models.api import error_response
from services.v2.document.dispatch_resolution import (
    DispatchResolutionExtractor,
    DispatchResolutionExtractorInput,
    DispatchResolutionExtractorOutput,
)
from . import router


@router.post("/dispatch-resolution/", response_model=DispatchResolutionExtractorOutput)
async def dispatch_resolution_post(
    file: UploadFile = File(..., description="Dispatch resolution PDF file"),
):
    """Handles the extraction of information from a dispatch resolution PDF file."""
    if file.content_type != "application/pdf":
        return error_response("Invalid file type", 400)

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        try:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
            extractor = DispatchResolutionExtractor(DispatchResolutionExtractorInput(file_path=temp_file_path))
            dispatch_resolution = extractor.extract()
        except Exception as e:
            return error_response(f"Internal error: {e}", 500)
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    return dispatch_resolution
