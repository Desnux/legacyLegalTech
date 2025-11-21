from fastapi import APIRouter, Body, Depends
from fastapi.responses import JSONResponse

from models.pydantic import ErrorResponse, DispatchResolutionStructure, JudicialCollectionDemandTextStructure, LegalSuggestion
from services.suggester import DispatchResolutionSuggester
from routers.base import get_api_key


router = APIRouter()


@router.post("/dispatch_resolution_by_structure/", response_model=list[LegalSuggestion], dependencies=[Depends(get_api_key)])
async def dispatch_resolution_by_structure_suggester(
    dispatch_resolution: DispatchResolutionStructure = Body(..., description="Dispatch resolution"),
    demand_text: JudicialCollectionDemandTextStructure | None = Body(None, description="Demand text"),
):
    try:
        suggester = DispatchResolutionSuggester()
        suggestions = suggester.generate_suggestions_from_structure(dispatch_resolution, demand_text)
    except Exception as e:
        error_response = ErrorResponse(error=f"Internal error: {e}", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    
    if suggestions is None:
        error_response = ErrorResponse(error="Could not generate dispatch resolution suggestions", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    return suggestions
