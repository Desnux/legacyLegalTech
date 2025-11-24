import os
import shutil
import tempfile
from fastapi import File, UploadFile

from models.api import error_response
from services.v2.document.demand_exception import (
    DemandExceptionExtractor,
    DemandExceptionExtractorInput,
    DemandExceptionExtractorOutput,
)
from . import router


@router.post("/demand-exception/", response_model=DemandExceptionExtractorOutput)
async def demand_exception_post(
    file: UploadFile = File(..., description="Demand exception PDF file"),
):
    """Handles the extraction of information from a demand exception PDF file."""
    if file.content_type != "application/pdf":
        return error_response("Invalid file type", 400)

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        try:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
            extractor = DemandExceptionExtractor(DemandExceptionExtractorInput(file_path=temp_file_path))
            demand_exception = extractor.extract()
        except Exception as e:
            return error_response(f"Internal error: {e}", 500)
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    return demand_exception
