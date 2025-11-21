import logging
from fastapi import APIRouter, Body, Depends
from fastapi.responses import JSONResponse

from models.api import DemandListGetRequest, DemandListGetResponse, ErrorResponse
from services.pjud import PJUDController
from routers.base import get_api_key


MAX_RETRIES = 3


router = APIRouter()


@router.post("/demand_list/", response_model=DemandListGetResponse, dependencies=[Depends(get_api_key)])
async def demand_list(
    input: DemandListGetRequest = Body(..., description="PJUD data"),
):
    controller = PJUDController()
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            controller_response = await controller.get_demand_list_from_pjud(input)
            if controller_response is not None:
                return controller_response
        except Exception as e:
            logging.warning(f"Attempt {attempt} to retrieve demand list failed with error: {e}")
            if attempt == MAX_RETRIES:
                error_response = ErrorResponse(error=f"Internal error: {e}", code=500)
                return JSONResponse(status_code=500, content=error_response.model_dump())
    
    error_response = ErrorResponse(error=f"Could not retrieve demand list after {MAX_RETRIES} retries", code=500)
    return JSONResponse(status_code=500, content=error_response.model_dump())
