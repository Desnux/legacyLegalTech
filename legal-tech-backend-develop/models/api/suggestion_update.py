from typing import Any, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class SuggestionUpdateRequest(BaseModel):
    """Request model for updating a suggestion."""
    
    name: Optional[str] = Field(None, description="Updated suggestion name")
    content: Optional[dict[str, Any]] = Field(None, description="Updated suggestion content")
    score: Optional[float] = Field(None, description="Updated suggestion score")


class SuggestionUpdateResponse(BaseModel):
    """Response model for suggestion update."""
    
    message: str = Field(..., description="Success message")
    suggestion_id: str = Field(..., description="Updated suggestion ID")
    updated_fields: list[str] = Field(..., description="List of fields that were updated")
