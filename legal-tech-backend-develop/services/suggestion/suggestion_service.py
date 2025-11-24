from typing import List
from uuid import UUID
from sqlmodel import select, Session

from models.sql import Case, CaseEvent, CaseEventSuggestion
from models.api.suggestion_update import SuggestionUpdateRequest, SuggestionUpdateResponse


class SuggestionService:
    """Service for managing case event suggestions."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def update_suggestion(
        self,
        case_id: UUID,
        event_id: UUID,
        suggestion_id: UUID,
        update_request: SuggestionUpdateRequest
    ) -> SuggestionUpdateResponse:
        """Updates a suggestion for a specific event."""
        
        # Verify case exists
        case_statement = select(Case).where(Case.id == case_id)
        case = self.session.exec(case_statement).first()
        if not case:
            raise ValueError(f"Case with ID {case_id} not found.")
        
        # Verify event exists and belongs to the case
        event_statement = select(CaseEvent).where(
            CaseEvent.id == event_id,
            CaseEvent.case_id == case_id
        )
        event = self.session.exec(event_statement).first()
        if not event:
            raise ValueError(f"Event with ID {event_id} not found for case {case_id}.")
        
        # Find the suggestion
        suggestion_statement = select(CaseEventSuggestion).where(
            CaseEventSuggestion.id == suggestion_id,
            CaseEventSuggestion.case_event_id == event_id
        )
        suggestion = self.session.exec(suggestion_statement).first()
        if not suggestion:
            raise ValueError(f"Suggestion with ID {suggestion_id} not found for event {event_id}.")
        
        # Track which fields are being updated
        updated_fields = []
        
        # Update fields if provided
        if update_request.name is not None:
            suggestion.name = update_request.name
            updated_fields.append("name")
        
        if update_request.content is not None:
            suggestion.content = update_request.content
            updated_fields.append("content")
        
        if update_request.score is not None:
            suggestion.score = update_request.score
            updated_fields.append("score")
        
        if not updated_fields:
            raise ValueError("No fields provided for update.")
        
        # Save changes
        self.session.add(suggestion)
        self.session.commit()
        self.session.refresh(suggestion)
        
        # Create response
        return SuggestionUpdateResponse(
            message="Suggestion updated successfully",
            suggestion_id=str(suggestion.id),
            updated_fields=updated_fields
        )
    
    def get_suggestions_for_event(self, event_id: UUID) -> List[CaseEventSuggestion]:
        """Gets all suggestions for a specific event."""
        statement = select(CaseEventSuggestion).where(
            CaseEventSuggestion.case_event_id == event_id
        )
        return self.session.exec(statement).all()
    
    def get_suggestion_by_id(self, suggestion_id: UUID) -> CaseEventSuggestion | None:
        """Gets a specific suggestion by ID."""
        statement = select(CaseEventSuggestion).where(
            CaseEventSuggestion.id == suggestion_id
        )
        return self.session.exec(statement).first()
