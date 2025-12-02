import logging
from datetime import datetime, timedelta
from fastapi import Body, Depends, File, Query, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlmodel import desc, func, select
from uuid import UUID

from database.ext_db import Session
from models.api.dispatch_start_response import DispatchStartEventResponse
from models.api.suggestion_update import SuggestionUpdateRequest, SuggestionUpdateResponse
from models.sql.case import CaseParty
from services.suggestion.suggestion_service import SuggestionService
from models.api import (
    CaseResponse,
    CaseDetailRequest,
    CaseDetailResponse,
    CaseStatsEventInformation,
    CaseStatsInformation,
    CaseStatsResponse,
    CourtInfo,
    DemandExceptionGenerationResponse,
    DispatchResolutionGenerationResponse,
    error_response,
    LegalCompromiseGenerationResponse,
    LitigantInformation,
    SuggestionRequest,
    SuggestionResponse,
    TribunalInfo,
    ActionRequest,
    ActionResponse,
    ActionsResponse,
)
from models.sql import Case, CaseDetail, CaseEvent, CaseEventSuggestion, CaseEventType, CaseStatus, Court, CourtCase, Document, Litigant, Tribunal, Action
from services.information import CaseRetriever, Statistics
from services.pjud import PJUDController
from services.tracker import CaseTracker
from services.v2.document.dispatch_start.event_manager import DispatchStartEventManager
from . import router
from middleware.auth_middleware import get_current_session


MAX_RETRIES = 3


# TODO: REMOVE WHEN TRACKED
def simulate_first_documents_event_date(case_id: str, base_date: datetime) -> str:
    try:
        case_uuid = UUID(case_id)
    except ValueError as e:
        raise ValueError(f"Invalid UUID format: {e}")
    uuid_int = case_uuid.int
    offset_days = (uuid_int % 16) + 5
    simulated_date = base_date + timedelta(days=offset_days)
    return simulated_date.isoformat()


@router.get("/cases/", response_model=list)
async def get_cases(
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(10, ge=1, description="Maximum number of records to return"),
    bank: str | None = Query(None, description="Filter by bank name"),
    status: list[str] | None = Query(None, description="Filter by status (multi-select)"),
    order_by: str | None = Query(None, description="Field to order by: title, created_at, or events"),
    order_direction: str | None = Query("asc", description="Order direction: 'asc' or 'desc'"),
    session: Session = Depends(get_current_session),
):
    """Returns all generated cases."""
    case_retriever = CaseRetriever()
    order_desc = order_direction.lower() == "desc" if order_direction else False
    try:
        case_count = case_retriever.get_case_count(session, status)
        cases = case_retriever.get_cases(session, skip, limit, status, order_by, order_desc)
        information: list[CaseStatsInformation] = []
        for case in cases:
            events = session.exec(select(CaseEvent).where(CaseEvent.case_id == case.id).order_by(CaseEvent.created_at)).all()
            final_events: list[CaseStatsEventInformation] = [
                CaseStatsEventInformation(type="documents")
            ]

            # TODO: REMOVE WHEN TRACKED
            if events and events[0].created_at:
                base_date = events[0].created_at
                simulated_date = simulate_first_documents_event_date(str(case.id), base_date)
                final_events[0].date = simulated_date

            for idx, sorted_event in enumerate(events):
                final_date = None
                if creation_date := sorted_event.created_at:
                    final_date = creation_date.isoformat()
                if sorted_event.type == CaseEventType.DEMAND_START and not "demand_start" in [t.type for t in final_events]:
                    final_events.append(
                        CaseStatsEventInformation(date=final_date, type="demand_start")
                    )
                elif sorted_event.type in [CaseEventType.DISPATCH_START] and not "dispatch_start" in [t.type for t in final_events]:
                    final_events.append(
                        CaseStatsEventInformation(date=final_date, type="dispatch_start")
                    )
                elif sorted_event.type == CaseEventType.DISPATCH_RESOLUTION and not "dipatch_resolution" in [t.type for t in final_events]:
                    final_events.append(
                        CaseStatsEventInformation(date=final_date, type="dipatch_resolution")
                    )
                elif sorted_event.type == CaseEventType.EXCEPTIONS and not "demand_exception" in [t.type for t in final_events]:
                    final_events.append(
                        CaseStatsEventInformation(date=final_date, type="demand_exception")
                    )
                elif sorted_event.type == CaseEventType.NOTIFICATION and not "notification" in [t.type for t in final_events]:
                    final_events.append(
                        CaseStatsEventInformation(date=final_date, type="notification")
                    )
                elif sorted_event.type == CaseEventType.TRANSLATION_EVACUATION and not "translation_evacuation" in [t.type for t in final_events]:
                    final_events.append(
                        CaseStatsEventInformation(date=final_date, type="translation_evacuation")
                    )
                elif sorted_event.type == CaseEventType.ASSET_SEIZURE_ORDER and not "asset_seizure" in [t.type for t in final_events]:
                    final_events.append(
                        CaseStatsEventInformation(date=final_date, type="asset_seizure")
                    )
                elif sorted_event.type == CaseEventType.SENTENCE and not "sentence" in [t.type for t in final_events]:
                    final_events.append(
                        CaseStatsEventInformation(date=final_date, type="sentence")
                    )
                #elif sorted_event.type in [CaseEventType.SENTENCE] and not "finished" in [t.type for t in final_events]:
                #    final_events.append(
                #        CaseStatsEventInformation(date=final_date, type="finished")
                #    )
                # elif idx == len(events) - 1 and case.status in [CaseStatus.ARCHIVED, CaseStatus.FINISHED] and not "finished" in [t.type for t in final_events]:
                #     final_events.append(
                #         CaseStatsEventInformation(date=final_date, type="finished")
                #     )

            # Get case detail with tribunal and court information
            case_detail = session.exec(
                select(CaseDetail, Tribunal, Court)
                .join(Tribunal, CaseDetail.tribunal_id == Tribunal.id)
                .join(Court, CaseDetail.court_id == Court.id)
                .where(CaseDetail.case_id == case.id)
            ).first()
            
            court_name = "To be assigned"
            tribunal_name = "To be assigned"
            case_detail_obj = None
            
            if case_detail:
                case_detail_obj, tribunal, court_obj = case_detail
                tribunal_name = tribunal.name
                court_name = court_obj.name

            # Convert litigants to LitigantInformation objects
            litigants_info = [
                LitigantInformation(
                    id=str(litigant.id),
                    name=litigant.name,
                    rut=litigant.rut,
                    address=litigant.address,
                    role=litigant.role.value,
                    simulated=litigant.simulated,
                    is_co_debtor=litigant.is_co_debtor,
                )
                for litigant in case.litigants
            ]

            information.append(
                CaseStatsInformation(
                    id=str(case.id),
                    title=case.title,
                    legal_subject=case.legal_subject.value,
                    winner=case.winner.value if case.winner else None,
                    status=case.status.value,
                    created_at=case.created_at.isoformat(),
                    latest_step=final_events[-1].type,
                    court=court_name,
                    rol=case_detail_obj.role if case_detail_obj else None,
                    year=case_detail_obj.year if case_detail_obj else None,
                    tribunal=tribunal_name,
                    events=final_events,
                    litigants=litigants_info,
                    simulated=case.simulated,
                    amount=case.amount,
                    amount_currency=case.amount_currency.value if case.amount_currency else None,
                )
            )
    except Exception as e:
        return error_response(f"Could not retrieve cases: {e}", 500, True)
    response = CaseStatsResponse(
        cases=information,
        case_count=case_count,
    )
    return JSONResponse(status_code=200, content=response.model_dump())


@router.get("/actions/", response_model=ActionsResponse)
async def get_all_actions(
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(10, ge=1, description="Maximum number of records to return"),
    session: Session = Depends(get_current_session),
):
    """Gets all actions created across all cases with pagination."""
    try:
        # Get total count
        count_statement = select(func.count(Action.id))
        total_count = session.exec(count_statement).first()
        
        # Get paginated actions
        statement = select(Action).offset(skip).limit(limit)
        actions = session.exec(statement).all()
        
        action_responses = []
        for action in actions:
            action_responses.append(ActionResponse(
                id=str(action.id),
                case_id=str(action.case_id),
                action_to_follow=action.action_to_follow,
                responsible=action.responsible,
                deadline=action.deadline,
                completed=action.completed,
                comment=action.comment
            ))
        
        response = ActionsResponse(
            actions=action_responses,
            total_count=total_count
        )
        serialized_response = jsonable_encoder(response)
        return JSONResponse(status_code=200, content=serialized_response)
        
    except Exception as e:
        return error_response(f"Could not retrieve all actions: {e}", 500, True)


@router.get("/{case_id}/", response_model=CaseResponse)
async def get_from_id(
    case_id: UUID,
    session: Session = Depends(get_current_session),
):
    """Returns the information of a case given a case UUID."""
    try:
        statement = select(Case).where(Case.id == case_id)
        case = session.exec(statement).first()
        if not case:
            return error_response(f"Case with ID {case_id} not found.", 404, True)
    except Exception as e:
        return error_response(f"Could not get case: {e}", 500, True)
    
    # Get case details with joins to court and tribunal (only the first one)
    try:
        details_statement = select(CaseDetail, Court, Tribunal).join(
            Court, CaseDetail.court_id == Court.id
        ).join(
            Tribunal, CaseDetail.tribunal_id == Tribunal.id
        ).where(CaseDetail.case_id == case_id)
        
        result = session.exec(details_statement).first()
        if result:
            case_detail, court, tribunal = result
            details_response = CaseDetailResponse(
                **case_detail.model_dump(),
                court=CourtInfo(**court.model_dump()),
                tribunal=TribunalInfo(**tribunal.model_dump())
            )
        else:
            details_response = None
    except Exception as e:
        logging.warning(f"Could not get case details: {e}")
        details_response = None
    
    try:
        stats_service = Statistics()
        stats = stats_service.get_probable_case_stats(session, case)
    except Exception as e:
        logging.warning(f"Could not get probable stats: {e}")
        stats = None
    
    # Get litigants for the case
    try:
        litigants_statement = select(Litigant).where(Litigant.case_id == case_id)
        litigants = session.exec(litigants_statement).all()
        litigants_info = [
            LitigantInformation(
                id=str(litigant.id),
                name=litigant.name,
                rut=litigant.rut,
                address=litigant.address,
                role=litigant.role.value,
                simulated=litigant.simulated,
                is_co_debtor=litigant.is_co_debtor,
            )
            for litigant in litigants
        ]
    except Exception as e:
        logging.warning(f"Could not get litigants: {e}")
        litigants_info = []
    
    case_response = CaseResponse(**case.model_dump(), stats=stats, details=details_response, litigants=litigants_info)
    serialized_case = jsonable_encoder(case_response)
    return JSONResponse(status_code=200, content=serialized_case)


@router.post("/{case_id}/details/", response_model=CaseDetailResponse)
async def create_case_detail(
    case_id: UUID,
    detail_request: CaseDetailRequest = Body(...),
    session: Session = Depends(get_current_session),
):
    """Create a new case detail for a specific case."""
    logging.info(f"Creating case detail for case_id: {case_id}")
    logging.info(f"Detail request: {detail_request}")
    try:
        # Verify that the case exists
        case_statement = select(Case).where(Case.id == case_id)
        case = session.exec(case_statement).first()
        if not case:
            return error_response(f"Case with ID {case_id} not found.", 404, True)
        
        # Verify that the court exists
        court_statement = select(Court).where(Court.id == detail_request.court_id)
        court = session.exec(court_statement).first()
        if not court:
            return error_response(f"Court with ID {detail_request.court_id} not found.", 404, True)
        
        # Verify that the tribunal exists
        tribunal_statement = select(Tribunal).where(Tribunal.id == detail_request.tribunal_id)
        tribunal = session.exec(tribunal_statement).first()
        if not tribunal:
            return error_response(f"Tribunal with ID {detail_request.tribunal_id} not found.", 404, True)
            
    except Exception as e:
        return error_response(f"Could not verify references: {e}", 500, True)
    
    try:
        # Create the case detail
        case_detail = CaseDetail(
            case_id=case_id,
            year=detail_request.year,
            role=detail_request.role,
            court_id=detail_request.court_id,
            tribunal_id=detail_request.tribunal_id
        )
        
        session.add(case_detail)
        session.flush()  # Flush to get the ID but don't commit yet
        
        if case.status != CaseStatus.ACTIVE:
            case.status = CaseStatus.ACTIVE
            session.add(case)
        
        event_manager = DispatchStartEventManager(case)
        event_manager.create_dispatch_start_event(
            session,
            content=None
        )
        
        session.commit()
        session.refresh(case_detail)
        
        # Get the created detail with joins to court and tribunal
        details_statement = select(CaseDetail, Court, Tribunal).join(
            Court, CaseDetail.court_id == Court.id
        ).join(
            Tribunal, CaseDetail.tribunal_id == Tribunal.id
        ).where(CaseDetail.id == case_detail.id)
        
        result = session.exec(details_statement).first()
        if result:
            case_detail_with_joins, court, tribunal = result
            detail_response = CaseDetailResponse(
                **case_detail_with_joins.model_dump(),
                court=CourtInfo(**court.model_dump()),
                tribunal=TribunalInfo(**tribunal.model_dump())
            )
        else:
            # Fallback if joins fail
            detail_response = CaseDetailResponse(**case_detail.model_dump())
        
        serialized_detail = jsonable_encoder(detail_response)
        return JSONResponse(status_code=201, content=serialized_detail)
        
    except Exception as e:
        session.rollback()
        return error_response(f"Could not create case detail: {e}", 500, True)


@router.get("/{case_id}/events/", response_model=list)
async def get_events_from_id(
    case_id: UUID,
    session: Session = Depends(get_current_session),
):
    """Returns the events of a case given a case UUID."""
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
        return error_response(f"Case events for case with ID {case_id} not found: {e}", 404, True)
    return JSONResponse(status_code=200, content=case_events_with_count)


@router.get("/{case_id}/event/{event_id}/documents/", response_model=list[Document])
async def get_event_documents_from_id(
    case_id: UUID,
    event_id: UUID,
    session: Session = Depends(get_current_session),
):
    """Returns the documents of an event given a case and event UUID."""
    try:
        statement = (
            select(Document)
            .where(Document.case_event_id == event_id)
            .order_by(Document.created_at)
        )
        documents = session.exec(statement).all()
    except Exception as e:
        return error_response(f"Could not get documents for case {case_id}: {e}", 500, True)
    serialized_documents = jsonable_encoder(documents)
    return JSONResponse(status_code=200, content=serialized_documents)


@router.get("/{case_id}/event/{event_id}/suggestions/", response_model=list[CaseEventSuggestion])
async def get_event_suggestions_from_id(
    case_id: UUID,
    event_id: UUID,
    session: Session = Depends(get_current_session),
):
    """Returns the suggestions generated for an event given a case and event UUID."""
    try:
        statement = (
            select(CaseEventSuggestion)
            .where(CaseEventSuggestion.case_event_id == event_id)
            .order_by(desc(CaseEventSuggestion.score))
        )
        suggestions = session.exec(statement).all()
    except Exception as e:
        return error_response(f"Could not get suggestions for case {case_id}: {e}", 500, True)
    serialized_documents = jsonable_encoder(suggestions)
    return JSONResponse(status_code=200, content=serialized_documents)


@router.post("/{case_id}/event/{event_id}/suggestions/", response_model=list[SuggestionResponse])
async def post_event_suggestions_from_id(
    case_id: UUID,
    event_id: UUID,
    data: SuggestionRequest = Body(..., description="PJUD Data"),
    file: UploadFile = File(..., description="Suggestion as PDF file"),
    session: Session = Depends(get_current_session),
):
    """Handles the selection of a suggestion generated for an event given a case and event UUID."""
    try:
        statement = select(Case).where(Case.id == case_id)
        case = session.exec(statement).first()
        if not case:
            return error_response(f"Case with ID {case_id} not found.", 404, True)
    except Exception as e:
        return error_response(f"Could not get case: {e}", 500, True)
    case_tracker = CaseTracker(case)
    try:
        statement = (
            select(CaseEvent)
            .where(CaseEvent.id == event_id)
        )
        event = session.exec(statement).first()
        if not event:
            return error_response(f"Case event with ID {event_id} not found.", 404, True)
        simulated = event.simulated
        statement = (
            select(CaseEventSuggestion)
            .where(CaseEventSuggestion.case_event_id == event_id, CaseEventSuggestion.id == data.id)
        )
        suggestion = session.exec(statement).first()
        if not suggestion:
            return error_response(f"Suggestion with ID {data.id} not found.", 404, True)
        statement = (
            select(CourtCase)
            .where(CourtCase.case_id == case_id, True if simulated else CourtCase.simulated == False)
        )
        court_case = session.exec(statement).first()
        if not court_case:
            return error_response(f"Could not find court data for case: {case_id}", 404, True)
        
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
                        return error_response(f"Internal error: {e}", 500)
            else:
                return error_response(f"Could not send suggestion after {MAX_RETRIES} retries", 500)
        else:
            controller_response = SuggestionResponse(message="Valid", status=200)

        try:
            case_tracker.register_suggestion(session, event, suggestion, simulated)
            pass
        except Exception as e:
            return error_response(f"Could not register suggestion in database ({type(e).__name__}): {e}", 500, True)

        return JSONResponse(status_code=200, content=controller_response.model_dump())
    except Exception as e:
        return error_response(f"Could not send suggestion for case {case_id}: {e}", 500, True)


@router.post("/{case_id}/simulate/demand-exception/", response_model=DemandExceptionGenerationResponse)
async def simulate_demand_exception_from_id(
    case_id: UUID,
    session: Session = Depends(get_current_session),
):
    """Simulates an exception given a case UUID."""
    try:
        statement = select(Case).where(Case.id == case_id)
        case = session.exec(statement).first()
        if not case:
            return error_response(f"Case with ID {case_id} not found.", 404, True)
    except Exception as e:
        return error_response(f"Could not get case: {e}", 500, True)
    statement = (
        select(CaseEvent)
        .where(CaseEvent.case_id == case_id, CaseEvent.type == CaseEventType.DEMAND_START, CaseEvent.next_event_id != None)
        .order_by(CaseEvent.created_at)
    )
    valid_case_events = session.exec(statement).all()
    if len(valid_case_events) == 0:
        return error_response("Case does not have dispatched demand text events", 400)
    case_tracker = CaseTracker(case)
    try:
        demand_exception_structure = case_tracker.simulate_demand_exception(session, valid_case_events[-1])
        if not demand_exception_structure:
            return error_response("Could not simulate demand exception", 500)
    except Exception as e:
        return error_response(f"Could not get simulate demand exception: {e}", 500, True)
    response = DemandExceptionGenerationResponse(structured_output=demand_exception_structure)
    return JSONResponse(status_code=200, content=response.model_dump())


@router.post("/{case_id}/simulate/dispatch-resolution/", response_model=DispatchResolutionGenerationResponse)
async def simulate_dispatch_resolution_from_id(
    case_id: UUID,
    session: Session = Depends(get_current_session),
):
    """Simulates a dispatch resolution given a case UUID."""
    try:
        statement = select(Case).where(Case.id == case_id)
        case = session.exec(statement).first()
        if not case:
            return error_response(f"Case with ID {case_id} not found.", 404, True)
    except Exception as e:
        return error_response(f"Could not get case: {e}", 500, True)
    statement = (
        select(CaseEvent)
        .where(CaseEvent.case_id == case_id, CaseEvent.type == CaseEventType.DEMAND_START, CaseEvent.next_event_id == None)
        .order_by(CaseEvent.created_at)
    )
    valid_case_events = session.exec(statement).all()
    if len(valid_case_events) == 0:
        return error_response("Case does not have unresolved demand text events", 400)
    case_tracker = CaseTracker(case)
    try:
        dispatch_resolution_structure = case_tracker.simulate_dispatch_resolution(session, valid_case_events[-1])
        if not dispatch_resolution_structure:
            return error_response("Could not simulate dispatch resolution", 500)
    except Exception as e:
        return error_response(f"Could not get simulate dispatch resolution: {e}", 500, True)
    response = DispatchResolutionGenerationResponse(structured_output=dispatch_resolution_structure)
    return JSONResponse(status_code=200, content=response.model_dump())


@router.post("/{case_id}/simulate/legal-compromise/", response_model=LegalCompromiseGenerationResponse)
async def simulate_legal_compromise_from_id(
    case_id: UUID,
    session: Session = Depends(get_current_session),
):
    """Simulates a legal compromise given a case UUID."""
    try:
        statement = select(Case).where(Case.id == case_id)
        case = session.exec(statement).first()
        if not case:
            return error_response(f"Case with ID {case_id} not found.", 404, True)
    except Exception as e:
        return error_response(f"Could not get case: {e}", 500, True)
    case_tracker = CaseTracker(case)
    try:
        legal_compromise_structure = case_tracker.simulate_legal_compromise(session, True)
        if not legal_compromise_structure:
            return error_response("Could not generate legal compromise", 500)
    except Exception as e:
        return error_response(f"Could not simulate legal compromise: {e}", 500, True)
    response = LegalCompromiseGenerationResponse(structured_output=legal_compromise_structure)
    return JSONResponse(status_code=200, content=response.model_dump())


@router.post("/{case_id}/actions/", response_model=ActionResponse)
async def create_action(
    case_id: UUID,
    action: ActionRequest = Body(...),
    session: Session = Depends(get_current_session),
):
    """Creates a new action for a specific case."""
    try:
        case = session.get(Case, case_id)
        if not case:
            return error_response(f"Case with ID {case_id} not found", 404, True)
        
        new_action = Action(
            case_id=case_id,
            action_to_follow=action.action_to_follow,
            responsible=action.responsible,
            deadline=action.deadline,
            comment=action.comment
        )
        
        session.add(new_action)
        session.commit()
        session.refresh(new_action)
        
        return ActionResponse(
            id=str(new_action.id),
            case_id=str(new_action.case_id),
            action_to_follow=new_action.action_to_follow,
            responsible=new_action.responsible,
            deadline=new_action.deadline,
            completed=new_action.completed,
            comment=new_action.comment
        )
        
    except Exception as e:
        session.rollback()
        return error_response(f"Could not create action: {e}", 500, True)


@router.get("/{case_id}/actions/", response_model=ActionsResponse)
async def get_case_actions(
    case_id: UUID,
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(10, ge=1, description="Maximum number of records to return"),
    session: Session = Depends(get_current_session),
):
    """Gets all actions for a specific case with pagination."""
    try:
        case = session.get(Case, case_id)
        if not case:
            return error_response(f"Case with ID {case_id} not found", 404, True)
        
        # Get total count for this case
        count_statement = select(func.count(Action.id)).where(Action.case_id == case_id)
        total_count = session.exec(count_statement).first()
        
        # Get paginated actions for this case
        statement = select(Action).where(Action.case_id == case_id).offset(skip).limit(limit)
        actions = session.exec(statement).all()
        
        action_responses = []
        for action in actions:
            action_responses.append(ActionResponse(
                id=str(action.id),
                case_id=str(action.case_id),
                action_to_follow=action.action_to_follow,
                responsible=action.responsible,
                deadline=action.deadline,
                completed=action.completed,
                comment=action.comment
            ))
        
        response = ActionsResponse(
            actions=action_responses,
            total_count=total_count
        )
        serialized_response = jsonable_encoder(response)
        return JSONResponse(status_code=200, content=serialized_response)
        
    except Exception as e:
        return error_response(f"Could not retrieve actions: {e}", 500, True)


@router.patch("/{case_id}/event/{event_id}/suggestion/{suggestion_id}/", response_model=SuggestionUpdateResponse)
async def update_suggestion(
    case_id: UUID,
    event_id: UUID,
    suggestion_id: UUID,
    update_request: SuggestionUpdateRequest = Body(...),
    session: Session = Depends(get_current_session),
) -> JSONResponse:
    """Updates a suggestion for a specific event."""
    try:
        suggestion_service = SuggestionService(session)
        response = suggestion_service.update_suggestion(
            case_id=case_id,
            event_id=event_id,
            suggestion_id=suggestion_id,
            update_request=update_request
        )
        
        serialized_response = jsonable_encoder(response)
        return JSONResponse(status_code=200, content=serialized_response)
        
    except ValueError as e:
        return error_response(str(e), 404, True)
    except Exception as e:
        session.rollback()
        return error_response(f"Error updating suggestion: {e}", 500, True)


