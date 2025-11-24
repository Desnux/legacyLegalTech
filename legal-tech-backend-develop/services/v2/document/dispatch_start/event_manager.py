from uuid import uuid4
from sqlmodel import select, Session
from models.sql import Case, CaseEvent, CaseEventType, CaseParty
from services.v2.document.base.event_manager import BaseEventManager


class DispatchStartEventManager(BaseEventManager):
    """Event manager for dispatch start events."""
    
    def __init__(self, case: Case):
        super().__init__(case)
    
    def create_dispatch_start_event(self, session: Session, content: str = None) -> CaseEvent:
        """Creates a dispatch start event for the case."""
        statement = (
            select(CaseEvent)
            .where(
                CaseEvent.case_id == self.case.id,
                CaseEvent.type == CaseEventType.DEMAND_START,
            )
            .order_by(CaseEvent.created_at)
        )
        demand_start_events = session.exec(statement).all()
        
        if len(demand_start_events) == 0:
            raise ValueError("Case does not have demand start events")
        
        demand_start_event = demand_start_events[-1]
        
        existing_dispatch = session.exec(
            select(CaseEvent).where(
                CaseEvent.case_id == self.case.id,
                CaseEvent.type == CaseEventType.DISPATCH_START,
            )
        ).first()
        
        if existing_dispatch:
            raise ValueError("Case already has a dispatch start event")
        
        dispatch_start_event = CaseEvent(
            id=uuid4(),
            case_id=self.case.id,
            case=self.case,
            title="Demanda Presentada",
            source=CaseParty.PLAINTIFFS,
            target=CaseParty.COURT,
            type=CaseEventType.DISPATCH_START,
            previous_event_id=demand_start_event.id,
            next_event_id=None,
            content=content,
            simulated=self.case.simulated,
        )
        
        # Primero guardar el DISPATCH_START
        session.add(dispatch_start_event)
        session.commit()
        session.refresh(dispatch_start_event)
        
        # Luego actualizar el DEMAND_START
        demand_start_event.next_event_id = dispatch_start_event.id
        session.add(demand_start_event)
        session.commit()
        
        return dispatch_start_event
    
    def _process_information(self, session: Session) -> None:
        """Process information for dispatch start event."""
        pass
    
    def _create_suggestions(self, session: Session) -> None:
        """Create suggestions for dispatch start event."""
        pass
