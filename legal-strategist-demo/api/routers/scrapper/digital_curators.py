import logging
from fastapi import APIRouter, Body, Depends
from fastapi.responses import JSONResponse

from models.api import DigitalCuratorsRequest, DigitalCuratorsResponse, ErrorResponse
from services.scrapper import DigitalCuratorsScrapper
from routers.base import get_api_key


MAX_RETRIES = 3


router = APIRouter()


@router.post("/digital-curators/", response_model=DigitalCuratorsResponse, dependencies=[Depends(get_api_key)])
async def digital_curators(
    input: DigitalCuratorsRequest = Body(..., description="Digital curators query"),
):
    scrapper = DigitalCuratorsScrapper()
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            scrapper_response = await scrapper.extract_information(input)
            return scrapper_response
        except Exception as e:
            logging.warning(f"Attempt {attempt} to extract information failed with error: {e}")
            if attempt == MAX_RETRIES:
                error_response = ErrorResponse(error=f"Internal error: {e}", code=500)
                return JSONResponse(status_code=500, content=error_response.model_dump())
    
    error_response = ErrorResponse(error=f"Could not extract information after {MAX_RETRIES} retries", code=500)
    return JSONResponse(status_code=500, content=error_response.model_dump())
