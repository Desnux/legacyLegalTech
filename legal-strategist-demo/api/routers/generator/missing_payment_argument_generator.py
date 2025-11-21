import logging
import os
import shutil
import tempfile

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import JSONResponse

from models.pydantic import ErrorResponse, MissingPaymentDocumentType, MissingPaymentArgument, MissingPaymentArgumentReason
from services.extractor import MissingPaymentReasonExtractor
from services.generator import MissingPaymentArgumentGenerator
from routers.base import get_api_key


router = APIRouter()


@router.post("/missing_payment_argument_by_file/", response_model=MissingPaymentArgument, dependencies=[Depends(get_api_key)])
async def missing_payment_argument_by_file_generator(
    reason: str = Form(..., description="Reason to argue missing payment", max_length=512),
    document_type: MissingPaymentDocumentType = Form(..., description="Document type"),
    seed: int = Form(0, description="Random generation seed for the IA"),
    file: UploadFile = File(..., description="Document PDF file"),
):
    if file.content_type != "application/pdf":
        error_response = ErrorResponse(error="Invalid file type", code=400)
        return JSONResponse(status_code=400, content=error_response.model_dump())

    try:
        reason_extractor = MissingPaymentReasonExtractor()
        structured_reason = reason_extractor.extract_from_text(reason)
        if structured_reason is None:
            raise ValueError("Null reason")
    except Exception as e:
        logging.warning(f"Could not extract missing payment reason: {e}")
        structured_reason = MissingPaymentArgumentReason(reason=reason)

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        try:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
            generator = MissingPaymentArgumentGenerator(structured_reason, seed)
            argument = generator.generate_from_file_path(temp_file_path, document_type)
        except Exception as e:
            error_response = ErrorResponse(error=f"Internal error: {e}", code=500)
            return JSONResponse(status_code=500, content=error_response.model_dump())
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    
    if argument is None:
        error_response = ErrorResponse(error="Could not generate argument from promissory note", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    return argument