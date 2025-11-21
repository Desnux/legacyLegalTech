from fastapi import APIRouter, Depends, Form
from fastapi.responses import JSONResponse

from models.pydantic import ErrorResponse, JudicialCollectionDemandTextInput
from services.extractor import DemandTextInputExtractor
from routers.base import get_api_key


router = APIRouter()


@router.post("/demand_text_input_by_text/", response_model=JudicialCollectionDemandTextInput, dependencies=[Depends(get_api_key)])
async def demand_text_by_input_text_extractor(
    text: str = Form(..., description="Demand text input raw text", max_length=32768),
):
    try:
        demand_text_input_extractor = DemandTextInputExtractor()
        demand_text_input = demand_text_input_extractor.extract_from_text(text)
    except Exception as e:
        error_response = ErrorResponse(error=f"Internal error (input extraction): {e}", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())

    if demand_text_input is None:
        error_response = ErrorResponse(error="Could not generate demand text", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    return demand_text_input
