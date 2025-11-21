import logging
from fastapi import APIRouter, Body, Depends
from fastapi.responses import JSONResponse

from models.api import DemandDeleteRequest, DemandDeleteResponse, DemandSendRequest, DemandSendResponse, ErrorResponse
from services.pjud import PJUDController
from routers.base import get_api_key


MAX_RETRIES = 3


router = APIRouter()


@router.post("/demand/", response_model=DemandSendResponse, dependencies=[Depends(get_api_key)])
async def demand_post(
    input: DemandSendRequest = Body(..., description="PJUD data"),
):
    controller = PJUDController()
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            controller_response = await controller.send_demand_to_court(input)
            if controller_response is not None:
                return controller_response
        except Exception as e:
            logging.warning(f"Attempt {attempt} to send demand failed with error: {e}")
            if attempt == MAX_RETRIES:
                error_response = ErrorResponse(error=f"Internal error: {e}", code=500)
                return JSONResponse(status_code=500, content=error_response.model_dump())
    
    error_response = ErrorResponse(error=f"Could not send demand after {MAX_RETRIES} retries", code=500)
    return JSONResponse(status_code=500, content=error_response.model_dump())


@router.delete("/demand/", response_model=DemandDeleteResponse, dependencies=[Depends(get_api_key)])
async def demand_delete(
    input: DemandDeleteRequest = Body(..., description="PJUD data"),
):
    controller = PJUDController()
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            controller_response = await controller.delete_demand(input)
            if controller_response is not None:
                return controller_response
        except Exception as e:
            logging.warning(f"Attempt {attempt} to delete demand failed with error: {e}")
            if attempt == MAX_RETRIES:
                error_response = ErrorResponse(error=f"Internal error: {e}", code=500)
                return JSONResponse(status_code=500, content=error_response.model_dump())
    
    error_response = ErrorResponse(error=f"Could not delete demand after {MAX_RETRIES} retries", code=500)
    return JSONResponse(status_code=500, content=error_response.model_dump())
