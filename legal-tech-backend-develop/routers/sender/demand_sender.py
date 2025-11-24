import logging
from fastapi import Body, Depends

from models.api import DemandDeleteRequest, DemandDeleteResponse, DemandSendRequest, DemandSendResponse, error_response
from services.pjud import PJUDController
from . import router


MAX_RETRIES = 3


@router.post("/demand/", response_model=DemandSendResponse)
async def demand_post(
    input: DemandSendRequest = Body(..., description="PJUD data"),
    controller: PJUDController = Depends(),
):
    """Handles the submission of a demand to a court through PJUD."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            if controller_response := await controller.send_demand_to_court(input):
                return controller_response
        except Exception as e:
            logging.warning(f"Attempt {attempt} to send demand failed with error: {e}")
            if attempt == MAX_RETRIES:
                return error_response(f"Internal error: {e}", 500)
    return error_response(f"Could not send demand after {MAX_RETRIES} retries", 500)


@router.delete("/demand/", response_model=DemandDeleteResponse)
async def demand_delete(
    input: DemandDeleteRequest = Body(..., description="PJUD data"),
    controller: PJUDController = Depends(),
):
    """Handles the deletion of a demand inside PJUD."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            if controller_response := await controller.delete_demand(input):
                return controller_response
        except Exception as e:
            logging.warning(f"Attempt {attempt} to delete demand failed with error: {e}")
            if attempt == MAX_RETRIES:
                return error_response(f"Internal error: {e}", 500)
    return error_response(f"Could not delete demand after {MAX_RETRIES} retries", 500)
