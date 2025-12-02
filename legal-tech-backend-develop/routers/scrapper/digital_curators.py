import logging
from fastapi import Body, Depends

from models.api import DigitalCuratorsRequest, DigitalCuratorsResponse, error_response
from services.scrapper import DigitalCuratorsScrapper
from . import router


MAX_RETRIES = 3


@router.post("/digital-curators/", response_model=DigitalCuratorsResponse)
async def digital_curators(
    input: DigitalCuratorsRequest = Body(..., description="Digital curators query"),
    scrapper: DigitalCuratorsScrapper = Depends(),
):
    """Handles the scrapping of information from "conservadoresdigitales.cl"."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            scrapper_response = await scrapper.extract_information(input)
            return scrapper_response
        except Exception as e:
            logging.warning(f"Attempt {attempt} to extract information failed with error: {e}")
            if attempt == MAX_RETRIES:
                return error_response(f"Internal error: {e}", 500)
    
    return error_response(f"Could not extract information after {MAX_RETRIES} retries", 500)
