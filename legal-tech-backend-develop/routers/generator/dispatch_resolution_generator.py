from fastapi import Body, Form

from models.api import error_response
from models.pydantic import JudicialCollectionDispatchResolution, JudicialCollectionDispatchResolutionInput
from services.generator import DispatchResolutionGenerator
from . import router


@router.post("/dispatch-resolution/", response_model=JudicialCollectionDispatchResolution)
async def dispatch_resolution_post(
    input: JudicialCollectionDispatchResolutionInput = Body(..., description="Required information"),
    demand_text: str = Form(..., description="Raw demand text to analyze", max_length=32768),
    seed: int = Form(0, description="Random generation seed for the IA"),
):
    """Handles the generation of a dispatch resolution."""
    try:
        generator = DispatchResolutionGenerator(input, seed)
        dispatch_resolution = generator.generate_from_text(demand_text)
    except Exception as e:
        return error_response(f"Internal error: {e}", 500)
    
    if dispatch_resolution is None:
        return error_response("Could not generate dispatch resolution", 500)
    return dispatch_resolution
