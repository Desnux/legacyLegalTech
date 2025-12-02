import logging
from fastapi import Depends, Query
from fastapi.responses import JSONResponse
from sqlmodel import select
from uuid import UUID

from database.ext_db import Session, get_session
from models.api import (
    error_response,
)
from models.sql import Tribunal
from models.pydantic.tribunal import TribunalResponse
from . import router


@router.get("", response_model=list[TribunalResponse])
async def get_all_tribunals(
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(10, ge=1, description="Maximum number of records to return"),
):
    """Returns all tribunals."""
    try:
        # Get database session
        session_gen = get_session()
        session = next(session_gen)
        
        try:
            # Query tribunals with pagination
            statement = select(Tribunal).offset(skip).limit(limit)
            tribunals = session.exec(statement).all()
            
            # Convert to response models
            result = []
            for tribunal in tribunals:
                result.append(TribunalResponse(
                    id=str(tribunal.id),
                    recepthor_id=str(tribunal.recepthor_id),
                    name=tribunal.name,
                    code=tribunal.code,
                    court_id=str(tribunal.court_id) if tribunal.court_id else None
                ))
            
            return result
        finally:
            session.close()
            
    except Exception as e:
        logging.error(f"Error getting tribunals: {e}")
        return error_response(f"Tribunals not found: {e}", 404, True)
