from sqlmodel import select
from uuid import uuid4, UUID

from database.ext_db import Session
from models.pydantic import (
    DispatchResolutionStructure,
    DocumentType,
    LegalSuggestion,
)
from models.sql import (
    Case,
    CaseEvent,
    CaseEventType,
    CaseParty,
    CourtCase,
)
from services.v2.document.base import (
    InformationBaseModel,
    ExtractorInputBaseModel,
    OutputBaseModel,
)
from services.v2.document.demand_text import DemandTextStructure
from services.v2.document.generic import (
    GenericEventManager,
    GenericExtractor,
)
from storage.s3_storage import S3Storage


class OtherEventManager(
    GenericEventManager[
        DispatchResolutionStructure,
        ExtractorInputBaseModel,
        InformationBaseModel,
        OutputBaseModel,
        DemandTextStructure,
    ]
):
    """Other event manager."""
    
    def __init__(self, case: Case, title: str, source: CaseParty, target: CaseParty, previous_event_id: UUID | None = None) -> None:
        super().__init__(case, DocumentType.OTHER, GenericExtractor, ExtractorInputBaseModel, DemandTextStructure)
        self.source = source
        self.target = target
        self.title = title
        self.previous_event_id = previous_event_id
    
    def create_from_file_path(
            self,
            session: Session,
            file_path: str
        ) -> tuple[InformationBaseModel, CaseEvent]:
        information = InformationBaseModel()
        new_event = self._process_information(session, information, file_path=file_path)
        return information, new_event    

    def _create_suggestions(
            self,
            session: Session,
            event: CaseEvent,
            information: InformationBaseModel,
            demand_text: DemandTextStructure,
        )-> list[LegalSuggestion] | None:
        return None

    def _process_information(
            self,
            session: Session,
            information: InformationBaseModel,
            *,
            file_path: str | None = None,
            key: str | None = None,
            structure: DispatchResolutionStructure | None = None,
        ) -> CaseEvent:
        if not (key or file_path) and not structure:
            raise ValueError("Either key or structure is required.")
        
        statement = (
            select(CaseEvent)
            .where(
                CaseEvent.case_id == self.case.id,
                CaseEvent.type == CaseEventType.DEMAND_START,
            )
            .order_by(CaseEvent.created_at)
        )
        valid_case_events = session.exec(statement).all()
        if len(valid_case_events) == 0:
            raise ValueError("Case does not have demand text events.")

        court_case_statement = select(CourtCase).where(
            CourtCase.case_id == self.case.id,
            CourtCase.simulated == self.case.simulated,
        )
        court_case = session.exec(court_case_statement).first()
        if not court_case:
            raise ValueError("Case without a valid court.")
          
        previous_event: CaseEvent | None = None
        if self.previous_event_id:
            statement = select(CaseEvent).where(
                CaseEvent.case_id == self.case.id,
                CaseEvent.id == self.previous_event_id,
            )
            previous_event = session.exec(statement).first()
        if not previous_event:
            self.previous_event_id = None

        try:
            new_case_event = CaseEvent(
                id=uuid4(),
                case_id=self.case.id,
                case=self.case,
                title=self.title,
                source=self.source,
                target=self.target,
                type=CaseEventType.OTHER,
                previous_event_id=self.previous_event_id,
                simulated=self.case.simulated,
            )
             
            if file_path and not key:   
                s3 = S3Storage()
                with open(file_path, "rb") as f:
                    file_content = f.read()
                key = f"case/{self.case.id}/event/{new_case_event.id}/annex_0.pdf"
                try:
                    s3.save(key, file_content)
                except Exception as e:
                    raise ValueError(f"Could not store document in S3: {e}")
            new_document = self._create_document(self.title, new_case_event, key, structure)

            session.add(new_document)
            session.add(new_case_event)
            session.add(court_case)
            session.commit()
            previous_event.next_event_id = new_case_event.id
            session.commit()
            return new_case_event
        except Exception as e:
            session.rollback()
            raise e
