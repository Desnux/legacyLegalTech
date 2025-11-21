from fastapi import APIRouter, Body, Depends, Form
from fastapi.responses import JSONResponse

from models.pydantic import ErrorResponse, JudicialCollectionDispatchResolution, JudicialCollectionDispatchResolutionInput
from services.generator import DispatchResolutionGenerator
from routers.base import get_api_key


router = APIRouter()


@router.post("/judicial_collection_dispatch_resolution_by_text/", response_model=JudicialCollectionDispatchResolution, dependencies=[Depends(get_api_key)])
async def judicial_collection_dispatch_resolution_by_text_generator(
    input: JudicialCollectionDispatchResolutionInput = Body(..., description="Required information"),
    demand_text: str = Form(..., description="Raw demand text to analyze", max_length=32768),
    seed: int = Form(0, description="Random generation seed for the IA"),
):
    try:
        generator = DispatchResolutionGenerator(input, seed)
        demand_text = generator.generate_from_text(demand_text)
    except Exception as e:
        error_response = ErrorResponse(error=f"Internal error: {e}", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    
    if demand_text is None:
        error_response = ErrorResponse(error="Could not generate dispatch resolution", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    return demand_text
