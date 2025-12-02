from datetime import datetime, date
from typing import Optional, List, Union
from pydantic import BaseModel


class FolioResponse(BaseModel):
    """Response model for individual folio"""
    id: int
    folio: int
    case_number: int
    year: int
    doc: Optional[str]
    stage: Optional[str]
    procedure: Optional[str]
    procedure_description: Optional[str]
    procedure_date: Optional[Union[date, str]]
    page: Optional[int]
    milestone: Optional[str]
    created_at: datetime
    updated_at: datetime
    is_active: bool
    scraping_session_id: str
    scraping_type: str


class PaginatedFoliosResponse(BaseModel):
    """Response model for paginated folios"""
    items: List[FolioResponse]
    total: int
    offset: int
    limit: int
    total_pages: int
    has_next: bool
    has_prev: bool


class FoliosStatsResponse(BaseModel):
    """Response model for folios statistics"""
    total_folios: int
    by_year: dict
    by_rol: dict
    by_milestone: dict
