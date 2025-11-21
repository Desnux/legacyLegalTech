from fastapi import APIRouter, Depends, Body, Form
from fastapi.responses import JSONResponse

from models.pydantic import ChatSimulation, ErrorResponse, Locale, SimulationInput
from services.simulator import ChatSimulator
from routers.base import get_api_key


DEFAULT_INPUT = SimulationInput(court_city="Santiago", creditors=[], debtors=[], co_debtors=[])


router = APIRouter()


@router.post("/chat_simulation/", response_model=ChatSimulation, dependencies=[Depends(get_api_key)])
async def chat_simulator(
    input: SimulationInput = Body(DEFAULT_INPUT, description="Optional attributes to set for the simulation"),
    seed: int = Form(0, description="Random generation seed for the IA"),
    locale: Locale = Form(Locale.ES_ES, description="Locale use for the generation"),
    api_key: str = Depends(get_api_key),
):
    try:
        simulator = ChatSimulator(input, seed, locale)
        simulation = simulator.simulate()
    except Exception as e:
        error_response = ErrorResponse(error=f"Internal error: {e}", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    
    if simulation is None:
        error_response = ErrorResponse(error="Could not generate chat simulation", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    return simulation
