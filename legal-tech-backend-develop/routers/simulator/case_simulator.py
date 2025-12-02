import os
import shutil
import tempfile
from fastapi import Body, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select
from uuid import UUID

from database.ext_db import Session
from models.api import error_response
from models.api.dispatch_start_response import DispatchStartEventCreateResponse, DispatchStartEventResponse
from models.api.dispatch_start_request import DispatchStartEventRequest
from models.sql import Case, CaseParty
from services.tracker import CaseTracker
from services.v2.document.generic import GenericEventManager
from services.v2.document.demand_exception import DemandExceptionEventManager
from services.v2.document.dispatch_resolution import DispatchResolutionEventManager
from services.v2.document.dispatch_start import DispatchStartEventManager
from services.v2.document.other import OtherEventManager
from middleware.auth_middleware import get_current_session
from models.sql.suggestion import CaseEventSuggestion
from . import router


def get_case(case_id: UUID, session: Session = Depends(get_current_session)) -> Case:
    """Returns a case from the database given a case UUID."""
    try:
        statement = select(Case).where(Case.id == case_id)
        case = session.exec(statement).first()
        if not case:
            raise HTTPException(status_code=404, detail=f"Case with ID {case_id} not found.")
        return case
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error while fetching case with ID {case_id}: {e}")


def handle_event_upload(file: UploadFile, session: Session, event_manager: GenericEventManager, include_suggestions: bool = False) -> JSONResponse:
    if file.content_type != "application/pdf":
        return error_response("Invalid file type", 400)

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file_path = temp_file.name
        try:
            shutil.copyfileobj(file.file, temp_file)
            information, event = event_manager.create_from_file_path(session, temp_file_path)
            event_manager.create_suggestions(session, event, information)
            
            response_content = {"message": "Valid", "code": 200}
            
            if include_suggestions:
                suggestions_statement = select(CaseEventSuggestion).where(
                    CaseEventSuggestion.case_event_id == event.id
                )
                suggestions = session.exec(suggestions_statement).all()
                
                if suggestions:
                    suggestions_data = []
                    for suggestion in suggestions:
                        suggestions_data.append({
                            "id": str(suggestion.id),
                            "name": suggestion.name,
                            "content": suggestion.content,
                            "score": suggestion.score,
                            "type": suggestion.type.value if suggestion.type else None
                        })
                    response_content["suggestions"] = suggestions_data
                response_content["event_id"] = str(event.id)
            
        except Exception as e:
            return error_response(f"Internal error: {e}", 500, True)
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    return JSONResponse(status_code=200, content=response_content)


@router.delete("/case/{case_id}/future-events/", response_model=dict)
async def delete_future_events_from_id(
    case: Case = Depends(get_case),
    session: Session = Depends(get_current_session),
) -> JSONResponse:
    """Handles the deletion of future events given a case UUID."""
    case_tracker = CaseTracker(case)
    try:
        case_tracker.clear_future_events(session)
    except Exception as e:
        return error_response(f"Could not delete future events: {e}", 500, True)
    return JSONResponse(status_code=200, content={"message": "Valid", "code": 200})


@router.put("/case/{case_id}/future-events/", response_model=dict)
async def put_future_events_from_id(
    case: Case = Depends(get_case),
    session: Session = Depends(get_current_session),
) -> JSONResponse:
    """Handles the simulation of future events given a case UUID."""
    case_tracker = CaseTracker(case)
    try:
        case_tracker.simulate_future_events(session)
    except Exception as e:
        return error_response(f"Could not simulate future events: {e}", 500, True)
    return JSONResponse(status_code=200, content={"message": "Valid", "code": 200})


@router.post("/case/{case_id}/demand-exception-event/", response_model=dict)
async def post_demand_exception_event(
    file: UploadFile = File(..., description="Demand exception PDF file"),
    case: Case = Depends(get_case),
    session: Session = Depends(get_current_session),
):
    """Creates a demand exception event from a file and returns suggestions."""
    event_manager = DemandExceptionEventManager(case)
    return handle_event_upload(file, session, event_manager, include_suggestions=True)


@router.post("/case/{case_id}/dispatch-start-event/", response_model=DispatchStartEventCreateResponse)
async def post_dispatch_start_event(
    request: DispatchStartEventRequest = Body(...),
    case: Case = Depends(get_case),
    session: Session = Depends(get_current_session),
) -> DispatchStartEventCreateResponse:
    """Creates a dispatch start event for a case."""
    try:
        event_manager = DispatchStartEventManager(case)
        dispatch_start_event = event_manager.create_dispatch_start_event(
            session,
            content=request.content
        )
        
        event_response = DispatchStartEventResponse(
            id=str(dispatch_start_event.id),
            title=dispatch_start_event.title,
            type=dispatch_start_event.type,
            source=dispatch_start_event.source,
            target=dispatch_start_event.target,
            created_at=dispatch_start_event.created_at,
            content=dispatch_start_event.content,
            simulated=dispatch_start_event.simulated,
            previous_event_id=str(dispatch_start_event.previous_event_id) if dispatch_start_event.previous_event_id else None,
            next_event_id=str(dispatch_start_event.next_event_id) if dispatch_start_event.next_event_id else None,
        )
        
        return DispatchStartEventCreateResponse(
            message="Dispatch start event created successfully",
            event=event_response
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating dispatch start event: {str(e)}")


@router.post("/case/{case_id}/dispatch-resolution-event/", response_model=dict)
async def post_dispatch_resolution_event(
    file: UploadFile = File(..., description="Dispatch resolution PDF file"),
    case: Case = Depends(get_case),
    session: Session = Depends(get_current_session),
) -> JSONResponse:
    """Creates a dispatch resolution event and event suggestions from a file."""
    event_manager = DispatchResolutionEventManager(case)
    return handle_event_upload(file, session, event_manager, include_suggestions=True)


@router.post("/case/{case_id}/other-event/", response_model=dict)
async def post_other_event(
    title: str = Form(..., description="Event title"),
    source: CaseParty = Form(..., description="Event source"),
    target: CaseParty = Form(..., description="Event target"),
    previous_event_id: UUID | None = Form(None, description="Event to tie into"),
    file: UploadFile = File(..., description="Event PDF file"),
    case: Case = Depends(get_case),
    session: Session = Depends(get_current_session),
) -> JSONResponse:
    """Creates an other event from a file."""
    event_manager = OtherEventManager(case, title, source, target, previous_event_id)
    return handle_event_upload(file, session, event_manager)
