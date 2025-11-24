from fastapi import Body

from models.api import error_response
from models.pydantic import LegalSuggestion
from services.v2.document.demand_text import DemandTextStructure
from services.v2.document.dispatch_resolution import DispatchResolutionInformation, DispatchResolutionSuggester
from . import router


@router.post("/dispatch-resolution/", response_model=list[LegalSuggestion])
async def dispatch_resolution_post(
    dispatch_resolution: DispatchResolutionInformation = Body(..., description="Dispatch resolution"),
    demand_text: DemandTextStructure | None = Body(None, description="Demand text"),
):
    """Handles the generation of suggestions for a dispatch resolution event."""
    try:
        suggester = DispatchResolutionSuggester()
        suggestions = suggester.generate_suggestions_from_structure(dispatch_resolution, demand_text)
    except Exception as e:
        return error_response(f"Internal error: {e}", 500)
    
    if suggestions is None:
        return error_response("Could not generate dispatch resolution suggestions", 500)
    return suggestions
