import logging
from datetime import datetime, date
from typing import Optional, List, Tuple
from fastapi import Query, Depends, HTTPException
from sqlmodel import Session, select, and_, or_, func

from models.sql.pjud_folio import PJUDFolio
from models.api.pjud_folio import FolioResponse, PaginatedFoliosResponse, FoliosStatsResponse
from database.ext_db import get_session
from . import router


def apply_pagination(
    query: select,
    offset: int,
    limit: int,
    session: Session
) -> Tuple[List[PJUDFolio], int, int, int, bool, bool]:
    total = len(session.exec(query).all())
    
    total_pages = (total + limit - 1) // limit if limit > 0 else 1
    
    paginated_query = query.order_by(PJUDFolio.created_at.desc()).offset(offset).limit(limit)
    
    items = session.exec(paginated_query).all()
    
    has_next = (offset + limit) < total
    has_prev = offset > 0
    
    return items, total, offset, limit, total_pages, has_next, has_prev


def build_folios_query(
    rol: Optional[str] = None,
    case_number: Optional[str] = None,
    year: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    hito: Optional[str] = None
) -> select:
    query = select(PJUDFolio).where(PJUDFolio.is_active == True)
    
    # Handle both rol (legacy) and case_number parameters
    case_filter = case_number or rol
    if case_filter:
        query = query.where(PJUDFolio.case_number == case_filter)
    
    if year:
        query = query.where(PJUDFolio.year == year)
    
    if start_date:
        query = query.where(PJUDFolio.created_at >= start_date)
    
    if end_date:
        end_datetime = datetime.combine(end_date, datetime.max.time())
        query = query.where(PJUDFolio.created_at <= end_datetime)
    
    if hito:
        query = query.where(PJUDFolio.milestone == hito)
    
    return query


@router.get("/folios/", response_model=PaginatedFoliosResponse)
async def get_folios(
    offset: int = Query(0, ge=0, description="Number of records to skip (starts from 0)"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return (max 100)"),
    rol: Optional[str] = Query(None, description="Filter by rol (legacy parameter)"),
    case_number: Optional[str] = Query(None, description="Filter by case number"),
    year: Optional[str] = Query(None, description="Filter by year"),
    start_date: Optional[date] = Query(None, description="Filter by start date (created_at)"),
    end_date: Optional[date] = Query(None, description="Filter by end date (created_at)"),
    hito: Optional[str] = Query(None, description="Filter by hito"),
    session: Session = Depends(get_session)
):
    try:
        query = build_folios_query(rol, case_number, year, start_date, end_date, hito)
        
        folios, total, offset, limit, total_pages, has_next, has_prev = apply_pagination(
            query, offset, limit, session
        )
        
        items = []
        for folio in folios:
            items.append(FolioResponse(
                id=folio.id,
                folio=folio.folio_number,
                case_number=folio.case_number,
                year=folio.year,
                doc=folio.document,
                stage=folio.stage,
                procedure=folio.procedure,
                procedure_description=folio.procedure_description,
                procedure_date=folio.procedure_date,
                page=folio.page,
                milestone=folio.milestone,
                created_at=folio.created_at,
                updated_at=folio.updated_at,
                is_active=folio.is_active,
                scraping_session_id=folio.scraping_session_id,
                scraping_type=folio.scraping_type
            ))
        
        return PaginatedFoliosResponse(
            items=items,
            total=total,
            offset=offset,
            limit=limit,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev
        )
        
    except Exception as e:
        logging.error(f"Error getting folios: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@router.get("/folios/stats/", response_model=FoliosStatsResponse)
async def get_folios_stats(
    session: Session = Depends(get_session)
):
    try:
        total_folios = len(session.exec(select(PJUDFolio).where(PJUDFolio.is_active == True)).all())
        
        years_query = select(PJUDFolio.year, func.count(PJUDFolio.id)).where(PJUDFolio.is_active == True).group_by(PJUDFolio.year)
        years_stats = session.exec(years_query).all()
        
        rols_query = select(PJUDFolio.case_number, func.count(PJUDFolio.id)).where(PJUDFolio.is_active == True).group_by(PJUDFolio.case_number)
        rols_stats = session.exec(rols_query).all()
        
        hitos_query = select(PJUDFolio.milestone, func.count(PJUDFolio.id)).where(PJUDFolio.is_active == True).group_by(PJUDFolio.milestone)
        hitos_stats = session.exec(hitos_query).all()
        
        return FoliosStatsResponse(
            total_folios=total_folios,
            by_year={year: count for year, count in years_stats},
            by_rol={rol: count for rol, count in rols_stats},
            by_milestone={hito: count for hito, count in hitos_stats if hito is not None}
        )
        
    except Exception as e:
        logging.error(f"Error getting folios stats: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@router.get("/folios/{folio_id}")
async def get_folio_by_id(
    folio_id: int,
    session: Session = Depends(get_session)
):
    try:
        folio = session.get(PJUDFolio, folio_id)
        if not folio:
            raise HTTPException(status_code=404, detail="Folio not found")
        
        return FolioResponse(
            id=folio.id,
            folio=folio.folio_number,
            case_number=folio.case_number,
            year=folio.year,
            doc=folio.document,
            stage=folio.stage,
            procedure=folio.procedure,
            procedure_description=folio.procedure_description,
            procedure_date=folio.procedure_date,
            page=folio.page,
            milestone=folio.milestone,
            created_at=folio.created_at,
            updated_at=folio.updated_at,
            is_active=folio.is_active,
            scraping_session_id=folio.scraping_session_id,
            scraping_type=folio.scraping_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting folio by ID: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")