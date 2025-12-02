from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from models.sql import CaseEventType, CaseParty


class DispatchStartEventResponse(BaseModel):
    """Response model for dispatch start event creation."""
    
    id: str = Field(..., description="Event ID")
    title: str = Field(..., description="Event title")
    type: CaseEventType = Field(..., description="Event type")
    source: CaseParty = Field(..., description="Event source party")
    target: CaseParty = Field(..., description="Event target party")
    created_at: datetime = Field(..., description="Event creation timestamp")
    content: Optional[str] = Field(None, description="Event content")
    simulated: bool = Field(..., description="Whether the event is simulated")
    previous_event_id: Optional[str] = Field(None, description="Previous event ID")
    next_event_id: Optional[str] = Field(None, description="Next event ID")


class DispatchStartEventCreateResponse(BaseModel):
    """Response model for dispatch start event creation endpoint."""
    
    message: str = Field(..., description="Success message")
    event: DispatchStartEventResponse = Field(..., description="Created event details")
