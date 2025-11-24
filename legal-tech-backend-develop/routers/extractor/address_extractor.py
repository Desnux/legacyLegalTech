from fastapi import Form

from models.api import error_response
from models.pydantic import PJUDAddress
from services.extractor import AddressExtractor
from . import router


@router.post("/address/", response_model=PJUDAddress)
async def address_text_post(
    text: str = Form(..., description="Address raw text", max_length=2048),
):
    """Handles the extraction of information from an address string."""
    try:
        address_extractor = AddressExtractor()
        address = address_extractor.extract_from_text(text)
    except Exception as e:
        return error_response(f"Could not extract information from address: {e}", 500)
    return address
