import logging
from fastapi import Body, Depends, Query
from typing import Dict, Any, Tuple, List, Optional
from uuid import UUID

from models.pydantic import CaseNotebookRequest, CaseNotebookResponse, PaginatedCaseNotebookResponse, CaseNotebookItem
from services.pjud.pjud_scrapper import PJUDScrapper
from . import router


MAX_RETRIES = 3

def apply_pagination_to_case_notebook(
    data: List[CaseNotebookItem],
    offset: int,
    limit: int
) -> Tuple[List[CaseNotebookItem], int, int, int, bool, bool]:
    """Apply pagination to case notebook data"""
    total = len(data)
    
    total_pages = (total + limit - 1) // limit if limit > 0 else 1
    
    # Apply pagination to the data
    paginated_data = data[offset:offset + limit]
    
    has_next = (offset + limit) < total
    has_prev = offset > 0
    
    return paginated_data, total, offset, limit, total_pages, has_next, has_prev
    

@router.post("/scraper/{case_id}/case-notebook", response_model=PaginatedCaseNotebookResponse)
async def extract_case_notebook(
    case_id: UUID,
    request: CaseNotebookRequest = Body(..., description="Case notebook extraction request"),
    offset: int = Query(0, ge=0, description="Number of records to skip (starts from 0)"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return (max 100)"),
    scrapper: PJUDScrapper = Depends(),
):
    """
    Extract case notebook information from PJUD for a specific case (RIT and year) with pagination.
    If case_id is provided, also downloads PDF from Hito 5 (Opone excepciones) and processes it
    to create demand exception event with suggestions.
    """
    logging.info(f"Extracting case notebook for case_id: {case_id}")

    scrapper._current_case_id = str(case_id)
    scrapper._current_case_number = request.case_number
    scrapper._current_year = request.year
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            scrapper_response = await scrapper.extract_case_notebook(request)
            
            # Apply pagination to the extracted data
            paginated_data, total, offset, limit, total_pages, has_next, has_prev = apply_pagination_to_case_notebook(
                scrapper_response.data, offset, limit
            )
            
            return PaginatedCaseNotebookResponse(
                message=scrapper_response.message,
                status=scrapper_response.status,
                data=paginated_data,
                total_items=total,
                offset=offset,
                limit=limit,
                total_pages=total_pages,
                has_next=has_next,
                has_prev=has_prev
            )
        except Exception as e:
            logging.warning(f"Attempt {attempt} to extract case notebook failed with error: {e}")
            if attempt == MAX_RETRIES:
                return PaginatedCaseNotebookResponse(
                    message=f"Internal error: {e}", 
                    status=500, 
                    data=[], 
                    total_items=0,
                    offset=offset,
                    limit=limit,
                    total_pages=0,
                    has_next=False,
                    has_prev=False
                )
    
    return PaginatedCaseNotebookResponse(
        message=f"Could not extract case notebook after {MAX_RETRIES} retries", 
        status=500, 
        data=[], 
        total_items=0,
        offset=offset,
        limit=limit,
        total_pages=0,
        has_next=False,
        has_prev=False
    )
