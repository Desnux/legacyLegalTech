from fastapi import Body

from models.api import error_response
from models.pydantic import LegalSuggestion
from services.v2.document.demand_exception import DemandExceptionInformation, DemandExceptionSuggester
from services.v2.document.demand_text import DemandTextStructure
from . import router


@router.post("/demand-exception/", response_model=list[LegalSuggestion])
async def demand_exception_post(
    demand_exception: DemandExceptionInformation = Body(..., description="Demand exception"),
    demand_text: DemandTextStructure | None = Body(None, description="Demand text"),
):
    """Handles the generation of suggestions for a demand exception event."""
    try:
        suggester = DemandExceptionSuggester()
        suggestions = suggester.generate_suggestions_from_structure(demand_exception, demand_text)
    except Exception as e:
        return error_response(f"Internal error: {e}", 500)
    
    if suggestions is None:
        return error_response("Could not generate demand exception suggestions", 500)
    return suggestions
