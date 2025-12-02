import os
import shutil
import tempfile
from fastapi import File, UploadFile

from models.api import error_response
from services.v2.document.coopeuch_report import (
    CoopeuchReportExtractor,
    CoopeuchReportExtractorInput,
    CoopeuchReportExtractorOutput,
)
from . import router


@router.post("/coopeuch-report/", response_model=CoopeuchReportExtractorOutput)
async def coopeuch_report_post(
    file: UploadFile = File(..., description="COOPEUCH report PDF file"),
):
    """Handles the extraction of information from a COOPEUCH report PDF file."""
    if file.content_type != "application/pdf":
        return error_response("Invalid file type", 400)
    
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        try:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
            extractor = CoopeuchReportExtractor(CoopeuchReportExtractorInput(file_path=temp_file_path))
            coopeuch_report = extractor.extract()
        except Exception as e:
            return error_response(f"Internal error: {e}", 500)
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    return coopeuch_report
