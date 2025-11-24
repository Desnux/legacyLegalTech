from fastapi import Body, Form

from models.api import error_response
from models.pydantic import JudicialCollectionDemandException, JudicialCollectionDemandExceptionInput
from services.generator import DemandExceptionGenerator
from . import router


@router.post("/demand-exception/", response_model=JudicialCollectionDemandException)
async def demand_exception_post(
    input: JudicialCollectionDemandExceptionInput = Body(..., description="Required information"),
    demand_text: str = Form(..., description="Raw demand text to analyze", max_length=32768),
    seed: int = Form(0, description="Random generation seed for the IA"),
):
    """Handles the generation of a demand exception."""
    try:
        generator = DemandExceptionGenerator(input, seed)
        demand_exception = generator.generate_from_text(demand_text)
    except Exception as e:
        return error_response(f"Internal error: {e}", 500)
    
    if demand_exception is None:
        return error_response("Could not generate demand exception", 500)
    return demand_exception
