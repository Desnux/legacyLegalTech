import logging
from uuid import UUID

from fastapi import APIRouter, Body, Depends, File, HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import desc, func, select

from database.ext_db import get_session, Session
from models.api import (
    DemandExceptionGenerationResponse,
    DemandTextGenerationResponse,
    DispatchResolutionGenerationResponse,
    ErrorResponse,
    LegalCompromiseGenerationResponse,
    SuggestionRequest,
    SuggestionResponse,
)
from models.sql import Case, CaseEvent, CaseEventSuggestion, CaseEventType, CourtCase, Document
from services.pjud import PJUDController
from services.tracker import CaseTracker
from routers.base import get_api_key


router = APIRouter()


def get_case(case_id: UUID, session: Session = Depends(get_session)) -> Case:
    try:
        statement = select(Case).where(Case.id == case_id)
        case = session.exec(statement).first()
        if not case:
            logging.warning(f"Case with ID {case_id} not found.")
            raise HTTPException(status_code=404, detail=f"Case with ID {case_id} not found.")
        return case
    except SQLAlchemyError as e:
        logging.error(f"Database error while fetching case with ID {case_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")


@router.delete("/case/{case_id}/future-events/", response_model=dict, dependencies=[Depends(get_api_key)])
async def delete_future_events_from_id(
    case: Case = Depends(get_case),
    session: Session = Depends(get_session),
):
    case_tracker = CaseTracker(case)
    try:
        case_tracker.clear_future_events(session)
    except Exception as e:
        logging.warning(f"Could not clear future events: {e}")
        error_response = ErrorResponse(error=f"Internal error: {e}", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    return JSONResponse(status_code=200, content={"message": "Valid", "code": 200})


@router.put("/case/{case_id}/future-events/", response_model=dict, dependencies=[Depends(get_api_key)])
async def put_future_events_from_id(
    case: Case = Depends(get_case),
    session: Session = Depends(get_session),
):
    case_tracker = CaseTracker(case)
    try:
        case_tracker.simulate_future_events(session)
    except Exception as e:
        logging.warning(f"Could not simulate future events: {e}")
        error_response = ErrorResponse(error=f"Internal error: {e}", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    return JSONResponse(status_code=200, content={"message": "Valid", "code": 200})
