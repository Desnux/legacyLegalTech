import os
import shutil
import tempfile
from fastapi import File, UploadFile

from models.api import error_response
from models.pydantic import JudicialCollectionDemandTextInput
from services.extractor import DemandTextExtractor
from . import router


@router.post("/demand-text/", response_model=JudicialCollectionDemandTextInput)
async def demand_text_post(
    file: UploadFile = File(..., description="Demand text PDF file"),
):
    """Handles the extraction of information from a demand text PDF file."""
    if file.content_type != "application/pdf":
        return error_response("Invalid file type", 400)

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        try:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
            extractor = DemandTextExtractor()
            demand_text_input = extractor.extract_from_file_path(temp_file_path)
        except Exception as e:
            return error_response(f"Internal error: {e}", 500)
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    if demand_text_input is None:
        return error_response("Could not extract information from demand text", 500)
    return demand_text_input
