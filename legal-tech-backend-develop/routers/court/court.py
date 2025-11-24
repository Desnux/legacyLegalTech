import logging
from fastapi import Depends, Query
from fastapi.responses import JSONResponse
from sqlmodel import select
from uuid import UUID

from database.ext_db import Session, get_session
from models.api import (
    error_response,
)
from models.sql import Court
from models.pydantic.court_response import CourtResponse
from . import router


@router.get("", response_model=list[CourtResponse])
async def get_courts(
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(10, ge=1, description="Maximum number of records to return"),
):
    """Returns all courts."""
    try:
        # Get database session
        session_gen = get_session()
        session = next(session_gen)
        
        try:
            # Query courts with pagination
            statement = select(Court).offset(skip).limit(limit)
            courts = session.exec(statement).all()
            
            # Convert to response models
            result = []
            for court in courts:
                result.append(CourtResponse(
                    id=str(court.id),
                    recepthor_id=str(court.recepthor_id),
                    name=court.name,
                    code=court.code
                ))
            
            return result
        finally:
            session.close()
            
    except Exception as e:
        logging.error(f"Error getting courts: {e}")
        return error_response(f"Courts not found: {e}", 404, True)
