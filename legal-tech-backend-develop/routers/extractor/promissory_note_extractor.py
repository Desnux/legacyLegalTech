import os
import shutil
import tempfile
from fastapi import File, UploadFile

from models.api import error_response
from services.v2.document.promissory_note import (
    PromissoryNoteExtractor,
    PromissoryNoteExtractorInput,
    PromissoryNoteExtractorOutput,
)
from . import router


@router.post("/promissory-note/", response_model=PromissoryNoteExtractorOutput)
async def promissory_note_post(
    file: UploadFile = File(..., description="Promissory note PDF file"),
):
    """Handles the extraction of information from a promissory note PDF file."""
    if file.content_type != "application/pdf":
        return error_response("Invalid file type", 400)
    
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        try:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
            extractor = PromissoryNoteExtractor(PromissoryNoteExtractorInput(file_path=temp_file_path))
            promissory_note = extractor.extract()
        except Exception as e:
            return error_response(f"Internal error: {e}", 500)
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    return promissory_note
