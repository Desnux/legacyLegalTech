import logging
from fastapi import Body, Depends

from models.api import DemandListGetRequest, DemandListGetResponse, error_response
from services.pjud import PJUDController
from . import router


MAX_RETRIES = 3


@router.post("/demand-list/", response_model=DemandListGetResponse)
async def demand_list_post(
    input: DemandListGetRequest = Body(..., description="PJUD data"),
    controller: PJUDController = Depends(),
):
    """Handles the extraction of demand information from PJUD."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            controller_response = await controller.get_demand_list_from_pjud(input)
            if controller_response is not None:
                return controller_response
        except Exception as e:
            logging.warning(f"Attempt {attempt} to retrieve demand list failed with error: {e}")
            if attempt == MAX_RETRIES:
                return error_response(f"Internal error: {e}", 500)
    
    return error_response(f"Could not retrieve demand list after {MAX_RETRIES} retries", 500)
