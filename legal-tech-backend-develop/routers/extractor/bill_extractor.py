import os
import shutil
import tempfile
from fastapi import File, UploadFile

from models.api import error_response
from services.v2.document.bill import (
    BillExtractor,
    BillExtractorInput,
    BillExtractorOutput,
)
from . import router


@router.post("/bill/", response_model=BillExtractorOutput)
async def bill_post(
    file: UploadFile = File(..., description="Bill PDF file"),
):
    """Handles the extraction of information from a bill PDF file."""
    if file.content_type != "application/pdf":
        return error_response("Invalid file type", 400)

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        try:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
            extractor = BillExtractor(BillExtractorInput(file_path=temp_file_path))
            bill = extractor.extract()
        except Exception as e:
            return error_response(f"Could not extract information from bill: {e}", 500)
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    return bill
