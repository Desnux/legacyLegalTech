from typing import Optional, Union
from pydantic import BaseModel, Field, field_validator


class CaseNotebookRequest(BaseModel):
    """Request model for case notebook extraction from PJUD"""
    case_number: str
    year: int
    tribunal_id: Union[int, str] = Field(1, description="Tribunal ID (can be int or string, validated against available tribunals)")
    debug: bool = False
    save_to_db: bool = False
    
    @field_validator('tribunal_id')
    @classmethod
    def validate_tribunal_id(cls, v):
        """Validate tribunal_id format."""
        # Convert to string for consistency
        tribunal_id_str = str(v)
        
        # Basic validation - should be a valid UUID format
        import re
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if not re.match(uuid_pattern, tribunal_id_str, re.IGNORECASE):
            raise ValueError(
                f"Invalid tribunal_id format '{v}'. "
                f"Must be a valid UUID. Use GET /v1/pjud/tribunals/ to see all available tribunals."
            )
        
        return tribunal_id_str


class CaseNotebookItem(BaseModel):
    """Individual item from case notebook extraction"""
    folio_number: int
    document: str
    stage: str
    procedure: str
    procedure_description: str
    procedure_date: str
    page: Optional[int] = None
    milestone: Optional[str] = None


class CaseNotebookResponse(BaseModel):
    """Response model for case notebook extraction"""
    message: str
    status: int
    data: list[CaseNotebookItem]
    total_items: int


class PaginatedCaseNotebookResponse(BaseModel):
    """Response model for paginated case notebook extraction"""
    message: str
    status: int
    data: list[CaseNotebookItem]
    total_items: int
    offset: int
    limit: int
    total_pages: int
    has_next: bool
    has_prev: bool
