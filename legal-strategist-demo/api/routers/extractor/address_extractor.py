from fastapi import APIRouter, Depends, Form
from fastapi.responses import JSONResponse

from models.pydantic import ErrorResponse, PJUDAddress
from services.extractor import AddressExtractor
from routers.base import get_api_key


router = APIRouter()


@router.post("/address_by_text/", response_model=PJUDAddress, dependencies=[Depends(get_api_key)])
async def address_text_extractor(
    text: str = Form(..., description="Address raw text", max_length=2048),
):
    try:
        address_extractor = AddressExtractor()
        address = address_extractor.extract_from_text(text)
    except Exception as e:
        error_response = ErrorResponse(error=f"Internal error (address extraction): {e}", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())

    if address is None:
        error_response = ErrorResponse(error="Could not extract address information", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    return address
