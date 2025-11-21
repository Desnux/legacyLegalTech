import logging
from uuid import UUID

from fastapi import APIRouter, Body, Depends, File, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
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


MAX_RETRIES = 3


router = APIRouter()


@router.get("/{case_id}/", response_model=Case, dependencies=[Depends(get_api_key)])
async def get_from_id(
    case_id: UUID,
    session: Session = Depends(get_session),
):
    try:
        statement = select(Case).where(Case.id == case_id)
        case = session.exec(statement).first()
        if not case:
            logging.warning(f"Case with ID {case_id} not found.")
            error_response = ErrorResponse(error=f"Case with ID {case_id} not found.", code=404)
            return JSONResponse(status_code=404, content=error_response.model_dump())
    except Exception as e:
        logging.warning(f"Could not get case: {e}")
        error_response = ErrorResponse(error=f"Internal error: {e}", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    serialized_case = jsonable_encoder(case)
    return JSONResponse(status_code=200, content=serialized_case)


@router.get("/{case_id}/events/", response_model=list, dependencies=[Depends(get_api_key)])
async def get_events_from_id(
    case_id: UUID,
    session: Session = Depends(get_session),
):
    try:
        statement = (
            select(CaseEvent, func.count(Document.id).label("document_count"))
            .join(Document, Document.case_event_id == CaseEvent.id, isouter=True)
            .where(CaseEvent.case_id == case_id)
            .group_by(CaseEvent.id)
            .order_by(CaseEvent.created_at)
        )
        case_events = session.exec(statement).all()
        case_events_with_count = [
            {**jsonable_encoder(case_event), "document_count": document_count}
            for case_event, document_count in case_events
        ]
    except Exception as e:
        logging.warning(f"Could not get case events: {e}")
        error_response = ErrorResponse(error=f"Case events for case with ID {case_id} not found.", code=404)
        return JSONResponse(status_code=404, content=error_response.model_dump())
    return JSONResponse(status_code=200, content=case_events_with_count)


@router.get("/{case_id}/event/{event_id}/documents/", response_model=list[Document], dependencies=[Depends(get_api_key)])
async def get_event_documents_from_id(
    case_id: UUID,
    event_id: UUID,
    session: Session = Depends(get_session),
):
    try:
        statement = (
            select(Document)
            .where(Document.case_event_id == event_id)
            .order_by(Document.created_at)
        )
        documents = session.exec(statement).all()
    except Exception as e:
        logging.warning(f"Could not get documents for case {case_id}: {e}")
        error_response = ErrorResponse(error=f"Internal error: {e}", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    serialized_documents = jsonable_encoder(documents)
    return JSONResponse(status_code=200, content=serialized_documents)


@router.get("/{case_id}/event/{event_id}/suggestions/", response_model=list[CaseEventSuggestion], dependencies=[Depends(get_api_key)])
async def get_event_suggestions_from_id(
    case_id: UUID,
    event_id: UUID,
    session: Session = Depends(get_session),
):
    try:
        statement = (
            select(CaseEventSuggestion)
            .where(CaseEventSuggestion.case_event_id == event_id)
            .order_by(desc(CaseEventSuggestion.score))
        )
        suggestions = session.exec(statement).all()
    except Exception as e:
        logging.warning(f"Could not get suggestions for case {case_id}: {e}")
        error_response = ErrorResponse(error=f"Internal error: {e}", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    serialized_documents = jsonable_encoder(suggestions)
    return JSONResponse(status_code=200, content=serialized_documents)


@router.post("/{case_id}/event/{event_id}/suggestions/", response_model=list[SuggestionResponse], dependencies=[Depends(get_api_key)])
async def post_event_suggestions_from_id(
    case_id: UUID,
    event_id: UUID,
    data: SuggestionRequest = Body(..., description="PJUD Data"),
    file: UploadFile = File(..., description="Suggestion as PDF file"),
    session: Session = Depends(get_session),
):
    try:
        statement = select(Case).where(Case.id == case_id)
        case = session.exec(statement).first()
        if not case:
            logging.warning(f"Case with ID {case_id} not found.")
            error_response = ErrorResponse(error=f"Case with ID {case_id} not found.", code=404)
            return JSONResponse(status_code=404, content=error_response.model_dump())
    except Exception as e:
        logging.warning(f"Could not get case: {e}")
        error_response = ErrorResponse(error=f"Internal error: {e}", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    case_tracker = CaseTracker(case)
    try:
        statement = (
            select(CaseEvent)
            .where(CaseEvent.id == event_id)
        )
        event = session.exec(statement).first()
        if not event:
            logging.warning(f"Case event with ID {event_id} not found.")
            error_response = ErrorResponse(error=f"Case event with ID {event_id} not found.", code=404)
            return JSONResponse(status_code=404, content=error_response.model_dump())
        simulated = event.simulated
        statement = (
            select(CaseEventSuggestion)
            .where(CaseEventSuggestion.case_event_id == event_id, CaseEventSuggestion.id == data.id)
        )
        suggestion = session.exec(statement).first()
        if not suggestion:
            logging.warning(f"Suggestion with ID {data.id} not found.")
            error_response = ErrorResponse(error=f"Suggestion with ID {data.id} not found.", code=404)
            return JSONResponse(status_code=404, content=error_response.model_dump())
        statement = (
            select(CourtCase)
            .where(CourtCase.case_id == case_id, True if simulated else CourtCase.simulated == False)
        )
        court_case = session.exec(statement).first()
        if not court_case:
            logging.warning(f"Could not find court data for case: {case_id}")
            error_response = ErrorResponse(error=f"Could not find court data for case: {case_id}", code=404)
            return JSONResponse(status_code=404, content=error_response.model_dump())
        
        controller_response: SuggestionResponse | None = None
        if not simulated:
            controller = PJUDController()
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    controller_response = await controller.send_suggestion_to_pjud(data, court_case, suggestion, file)
                    break
                except Exception as e:
                    logging.warning(f"Attempt {attempt} to send suggestion failed with error: {e}")
                    if attempt == MAX_RETRIES:
                        error_response = ErrorResponse(error=f"Internal error: {e}", code=500)
                        return JSONResponse(status_code=500, content=error_response.model_dump())
            else:
                error_response = ErrorResponse(error=f"Could not send suggestion after {MAX_RETRIES} retries", code=500)
                return JSONResponse(status_code=500, content= error_response.model_dump())
        else:
            controller_response = SuggestionResponse(message="Valid", status=200)

        try:
            case_tracker.register_suggestion(session, event, suggestion, simulated)
            pass
        except Exception as e:
            logging.error(f"Could not register suggestion in database ({type(e).__name__}): {e}")
            error_response = ErrorResponse(error="Could not register suggestion in database:", code=500)
            return JSONResponse(status_code=500, content=error_response.model_dump())

        return JSONResponse(status_code=200, content=controller_response.model_dump())
    except Exception as e:
        logging.warning(f"Could not send suggestion for case {case_id}: {e}")
        error_response = ErrorResponse(error=f"Internal error: {e}", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())


@router.post("/{case_id}/simulate/demand-exception/", response_model=DemandExceptionGenerationResponse, dependencies=[Depends(get_api_key)])
async def simulate_demand_exception_from_id(
    case_id: UUID,
    session: Session = Depends(get_session),
):
    try:
        statement = select(Case).where(Case.id == case_id)
        case = session.exec(statement).first()
        if not case:
            logging.warning(f"Case with ID {case_id} not found.")
            error_response = ErrorResponse(error=f"Case with ID {case_id} not found.", code=404)
            return JSONResponse(status_code=404, content=error_response.model_dump())
    except Exception as e:
        logging.warning(f"Could not get case: {e}")
        error_response = ErrorResponse(error=f"Internal error: {e}", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    statement = (
        select(CaseEvent)
        .where(CaseEvent.case_id == case_id, CaseEvent.type == CaseEventType.DEMAND_START, CaseEvent.next_event_id != None)
        .order_by(CaseEvent.created_at)
    )
    valid_case_events = session.exec(statement).all()
    if len(valid_case_events) == 0:
        error_response = ErrorResponse(error="Case does not have dispatched demand text events", code=400)
        return JSONResponse(status_code=400, content=error_response.model_dump())
    case_tracker = CaseTracker(case)
    try:
        demand_exception_structure = case_tracker.simulate_demand_exception(session, valid_case_events[-1])
        if not demand_exception_structure:
            error_response = ErrorResponse(error="Could not simulate demand exception", code=500)
            return JSONResponse(status_code=500, content=error_response.model_dump())
    except Exception as e:
        logging.warning(f"Could not get simulate demand exception: {e}")
        error_response = ErrorResponse(error=f"Internal error: {e}", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    response = DemandExceptionGenerationResponse(structured_output=demand_exception_structure)
    return JSONResponse(status_code=200, content=response.model_dump())


@router.post("/{case_id}/simulate/dispatch-resolution/", response_model=DispatchResolutionGenerationResponse, dependencies=[Depends(get_api_key)])
async def simulate_dispatch_resolution_from_id(
    case_id: UUID,
    session: Session = Depends(get_session),
):
    try:
        statement = select(Case).where(Case.id == case_id)
        case = session.exec(statement).first()
        if not case:
            logging.warning(f"Case with ID {case_id} not found.")
            error_response = ErrorResponse(error=f"Case with ID {case_id} not found.", code=404)
            return JSONResponse(status_code=404, content=error_response.model_dump())
    except Exception as e:
        logging.warning(f"Could not get case: {e}")
        error_response = ErrorResponse(error=f"Internal error: {e}", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    statement = (
        select(CaseEvent)
        .where(CaseEvent.case_id == case_id, CaseEvent.type == CaseEventType.DEMAND_START, CaseEvent.next_event_id == None)
        .order_by(CaseEvent.created_at)
    )
    valid_case_events = session.exec(statement).all()
    if len(valid_case_events) == 0:
        error_response = ErrorResponse(error="Case does not have unresolved demand text events", code=400)
        return JSONResponse(status_code=400, content=error_response.model_dump())
    case_tracker = CaseTracker(case)
    try:
        dispatch_resolution_structure = case_tracker.simulate_dispatch_resolution(session, valid_case_events[-1])
        if not dispatch_resolution_structure:
            error_response = ErrorResponse(error="Could not simulate dispatch resolution", code=500)
            return JSONResponse(status_code=500, content=error_response.model_dump())
    except Exception as e:
        logging.warning(f"Could not get simulate dispatch resolution: {e}")
        error_response = ErrorResponse(error=f"Internal error: {e}", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    response = DispatchResolutionGenerationResponse(structured_output=dispatch_resolution_structure)
    return JSONResponse(status_code=200, content=response.model_dump())


@router.post("/{case_id}/simulate/legal-compromise/", response_model=LegalCompromiseGenerationResponse, dependencies=[Depends(get_api_key)])
async def simulate_legal_compromise_from_id(
    case_id: UUID,
    session: Session = Depends(get_session),
):
    try:
        statement = select(Case).where(Case.id == case_id)
        case = session.exec(statement).first()
        if not case:
            logging.warning(f"Case with ID {case_id} not found.")
            error_response = ErrorResponse(error=f"Case with ID {case_id} not found.", code=404)
            return JSONResponse(status_code=404, content=error_response.model_dump())
    except Exception as e:
        logging.warning(f"Could not get case: {e}")
        error_response = ErrorResponse(error=f"Internal error: {e}", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    case_tracker = CaseTracker(case)
    try:
        legal_compromise_structure = case_tracker.simulate_legal_compromise(session, True)
        if not legal_compromise_structure:
            error_response = ErrorResponse(error="Could not generate legal compromise", code=500)
            return JSONResponse(status_code=500, content=error_response.model_dump())
    except Exception as e:
        logging.warning(f"Could not simulate legal compromise: {e}")
        error_response = ErrorResponse(error=f"Internal error: {e}", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    response = LegalCompromiseGenerationResponse(structured_output=legal_compromise_structure)
    return JSONResponse(status_code=200, content=response.model_dump())


@router.post("/create-from-demand-text/", response_model=Case, dependencies=[Depends(get_api_key)])
async def create_from_demand_text_post(
    data: DemandTextGenerationResponse = Body(..., description="Demand text information"),
    session: Session = Depends(get_session),
):
    tracker = CaseTracker()
    try:
        case: Case = tracker.create_case_from_demand_text(session, data)
    except Exception as e:
        logging.warning(f"Could not create case from demand text: {e}")
        error_response = ErrorResponse(error=f"Internal error: {e}", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    serialized_case = jsonable_encoder(case)
    return JSONResponse(status_code=200, content=serialized_case)
