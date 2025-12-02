from datetime import datetime, time
from fastapi import Depends, Query
from fastapi.responses import JSONResponse, StreamingResponse
from sqlmodel import Session, select

from database.ext_db import Session
from models.api import error_response
from models.api.information import (
    CaseStatsResponse,
    CaseStatsInformation,
    CaseStatsEventInformation,
)
from models.sql import Case, CaseEvent, CaseEventType, CaseStatus, CourtCase, CaseParty, CaseStatsEvent, CaseDetail, Tribunal, Court
from services.information import CaseRetriever, Statistics
from middleware.auth_middleware import get_current_session
from . import router


@router.get("/cases/", response_model=CaseStatsResponse)
async def get_cases(
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(10, ge=1, description="Maximum number of records to return"),
    bank: str | None = Query(None, description="Filter by bank name"),
    status: list[str] | None = Query(None, description="Filter by status (multi-select)"),
    order_by: str | None = Query(None, description="Field to order by: title, created_at, or events"),
    order_direction: str | None = Query("asc", description="Order direction: 'asc' or 'desc'"),
    session: Session = Depends(get_current_session),
):
    """Returns statistical information about cases."""
    statistics = Statistics()
    order_desc = order_direction.lower() == "desc" if order_direction else False
    try:
        case_count = statistics.get_case_count(session, bank, status)
        cases = statistics.get_cases(
            session,
            skip,
            limit,
            bank,
            status,
            order_by,
            order_desc,
        )
        information: list[CaseStatsInformation] = []
        for case in cases:
            status = "active"
            if case.legal_stage in ("draft", "finished", "archived"):
                status = case.legal_stage
            
            created_at: str | None = None
            events = statistics.get_case_events(session, case.id)
            sorted_events: list[CaseStatsEvent] = sorted(
                (e for e in events if e.creation_date is not None),
                key=lambda e: e.creation_date
            )
            if sorted_events:
                earliest = sorted_events[0].creation_date
                created_at = datetime.combine(earliest, time(0, 0, 0)).isoformat()
            final_events: list[CaseStatsEventInformation] = [
                CaseStatsEventInformation(type="documents")
            ]
            for idx, sorted_event in enumerate(sorted_events):
                final_date = None
                if creation_date := sorted_event.creation_date:
                    final_date = datetime.combine(creation_date, time(0, 0, 0)).isoformat()
                if sorted_event.type == "demand_start" and not "demand_text" in [t.type for t in final_events]:
                    final_events.append(
                        CaseStatsEventInformation(date=final_date, type="demand_text")
                    )
                elif sorted_event.type in ["receiver_action", "payment_request"] and not "notification" in [t.type for t in final_events]:
                    final_events.append(
                        CaseStatsEventInformation(date=final_date, type="notification")
                    )
                elif sorted_event.type in ["embargo", "auction", "auctioneer_designation"] and not "asset_seizure" in [t.type for t in final_events]:
                    final_events.append(
                        CaseStatsEventInformation(date=final_date, type="asset_seizure")
                    )
                elif sorted_event.type in ["legal_sentence", "sentence_notification", "compromise"] and not "finished" in [t.type for t in final_events]:
                    final_events.append(
                        CaseStatsEventInformation(date=final_date, type="finished")
                    )
                elif idx == len(sorted_events) - 1 and status in ["finished", "archived"] and not "finished" in [t.type for t in final_events]:
                    final_events.append(
                        CaseStatsEventInformation(date=final_date, type="finished")
                    )

            case_detail_obj = session.exec(
                select(CaseDetail, Tribunal, Court)
                .join(Tribunal, CaseDetail.tribunal_id == Tribunal.id)
                .join(Court, CaseDetail.court_id == Court.id)
                .where(CaseDetail.case_id == case.id)
            ).first()
            court = "To be assigned"
            tribunal = "To be assigned"
            if case_detail_obj:
                tribunal_obj, court_obj = case_detail_obj
                tribunal = tribunal_obj.name
                court = court_obj.name
                
            if number := case.court_number:
                court = f"{number}° Juzgado de {court}"
            else:
                court = f"Juzgado de {court}"
            winner: CaseParty | None = None
            if result := case.result:
                match result.lower():
                    case "sentence_for_plaintiffs":
                        winner = CaseParty.PLAINTIFFS.value
                    case "sentence_for_defendants":
                        winner = CaseParty.DEFENDANTS.value
                    case "settlement":
                        winner = CaseParty.PLAINTIFFS.value
                    case "suspended":
                        winner = CaseParty.DEFENDANTS.value
                    case "desisted":
                        winner = CaseParty.DEFENDANTS.value
            information.append(
                CaseStatsInformation(
                    id=str(case.id),
                    title=case.title,
                    legal_subject=case.case_type,
                    winner=winner,
                    status=status,
                    created_at=created_at,
                    latest_step=final_events[-1].type,
                    court=court,
                    tribunal=tribunal,
                    events=final_events,
                    simulated=False,
                )
            )
    except Exception as e:
        return error_response(f"Could not retrieve cases: {e}", 500, True)
    response = CaseStatsResponse(
        cases=information,
        case_count=case_count,
    )
    return JSONResponse(status_code=200, content=response.model_dump())


@router.get(
    "/cases/{bank}/csv/",
    responses={
        200: {
            "content": {"application/zip": {}},
            "description": "Returns a zip file",
        }
    },
    response_class=StreamingResponse,
)
async def get_cases_csv(bank: str, session: Session = Depends(get_current_session)):
    """Returns statistical information about bank cases as csv files."""
    statistics = Statistics()
    zip_buffer = statistics.get_cases_csv(session, bank)
    return StreamingResponse(zip_buffer, media_type="application/zip", headers={
        "Content-Disposition": "attachment; filename=casos.zip"
    })
