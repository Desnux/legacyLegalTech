import logging
from uuid import UUID
from fastapi import Query

from database.ext_db import get_session
from models.api import error_response, ReceptorResponse
from services.receptor.receptor_service import (
    get_receptors as get_receptors_service,
    get_receptors_by_tribunal as get_receptors_by_tribunal_service
)
from . import router


@router.get("/", response_model=list[ReceptorResponse])
async def get_receptors(
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(10, ge=1, description="Maximum number of records to return"),
):
    """Returns all receptors with their tribunal associations."""
    try:
        session_gen = get_session()
        session = next(session_gen)
        
        return get_receptors_service(session, skip, limit)
    except Exception as e:
        logging.error(f"Error getting receptors: {e}")
        return error_response(f"Receptors not found: {e}", 404, True)


@router.get("/tribunal/{tribunal_id}/", response_model=list[ReceptorResponse])
async def get_receptors_by_tribunal(
    tribunal_id: UUID,
):
    """Returns all receptors associated with a specific tribunal."""
    try:
        session_gen = get_session()
        session = next(session_gen)
        
        return get_receptors_by_tribunal_service(session, tribunal_id)
    except Exception as e:
        logging.error(f"Error getting receptors by tribunal: {e}")
        return error_response(f"Receptors not found: {e}", 404, True)