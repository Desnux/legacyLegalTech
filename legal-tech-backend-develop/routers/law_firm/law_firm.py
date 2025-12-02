import logging
from fastapi import Body, Depends, Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from database.ext_db import Session, get_session
from models.api import error_response
from models.pydantic.law_firm import LawFirmCreate, LawFirmResponse
from services.lawfirm import lawfirm_service
from . import router


@router.post("", response_model=LawFirmResponse)
async def create_law_firm_endpoint(
    law_firm_data: LawFirmCreate = Body(..., description="Law firm data"),
    session: Session = Depends(get_session)
):
    """Create a new law firm in the database."""
    try:
        response = lawfirm_service.create_law_firm(session, law_firm_data)
        serialized_response = jsonable_encoder(response)
        return JSONResponse(status_code=201, content=serialized_response)
        
    except Exception as e:
        logging.error(f"Error creating law firm: {e}")
        return error_response(f"Could not create law firm: {e}", 500, True)


@router.get("", response_model=list[LawFirmResponse])
async def get_all_law_firms_endpoint(
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(10, ge=1, description="Maximum number of records to return"),
    session: Session = Depends(get_session)
):
    """Returns all law firms."""
    try:
        result = lawfirm_service.get_all_law_firms(session, skip, limit)
        return result
        
    except Exception as e:
        logging.error(f"Error getting law firms: {e}")
        return error_response(f"Law firms not found: {e}", 404, True)

