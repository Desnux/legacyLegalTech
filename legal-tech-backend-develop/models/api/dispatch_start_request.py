from typing import Optional
from pydantic import BaseModel, Field


class DispatchStartEventRequest(BaseModel):
    """Request model for dispatch start event creation."""
    
    content: Optional[str] = Field(None, description="Optional notes or additional information about the dispatch")
