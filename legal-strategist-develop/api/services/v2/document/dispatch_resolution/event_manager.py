from sqlmodel import select
from uuid import uuid4

from database.ext_db import Session
from models.pydantic import (
    DefendantType,
    DemandTextCorrectionInput,
    DispatchResolutionStructure,
    DocumentType,
    LegalResponseInput,
    LegalSuggestion,
    SuggestionType,
)
from models.sql import (
    Case,
    CaseEvent,
    CaseEventSuggestion,
    CaseEventType,
    CaseParty,
    CaseStatus,
    CourtCase,
)
from services.v2.document.compromise import (
    CompromiseGenerator,
    CompromiseGeneratorInput,
)
from services.v2.document.demand_text import DemandTextStructure
from services.v2.document.generic import GenericEventManager
from services.v2.document.withdrawal import (
    WithdrawalGenerator,
    WithdrawalGeneratorInput,
)
from storage.s3_storage import S3Storage
from .extractor import DispatchResolutionExtractor
from .models import (
    DispatchResolutionInformation,
    DispatchResolutionExtractorInput,
    DispatchResolutionExtractorOutput,
)
from .suggester import DispatchResolutionSuggester


class DispatchResolutionEventManager(
    GenericEventManager[
        DispatchResolutionStructure,
        DispatchResolutionExtractorInput,
        DispatchResolutionInformation,
        DispatchResolutionExtractorOutput,
        DemandTextStructure,
    ]
):
    """Dispatch resolution event manager."""
    
    def __init__(self, case: Case) -> None:
        super().__init__(case, DocumentType.DISPATCH_RESOLUTION, DispatchResolutionExtractor, DispatchResolutionExtractorInput, DemandTextStructure)

    def _create_suggestions(
            self,
            session: Session,
            event: CaseEvent,
            information: DispatchResolutionInformation,
            demand_text: DemandTextStructure,
        )-> list[LegalSuggestion] | None:
        from services.generator import DemandTextCorrectionGenerator, LegalResponseGenerator
        court_case_statement = select(CourtCase).where(
            CourtCase.case_id == self.case.id,
            CourtCase.simulated == self.case.simulated,
        )
        court_case = session.exec(court_case_statement).first()
        if not court_case:
            raise ValueError("Case without a valid court.")
        plaintiffs = self._get_plaintiffs(session)
        sponsoring_attorneys = self._get_sponsoring_attorneys(session)
        defendants = self._get_defendants(session)
        defendant_attorneys = self._get_defendant_attorneys(session)
        
        suggester = DispatchResolutionSuggester()
        suggestions = suggester.generate_suggestions_from_structure(information, demand_text)
        if not suggestions:
            suggestions = []
        
        probable_stats = self._get_probable_stats(session)
        if not any(suggestion.suggestion_type == SuggestionType.COMPROMISE for suggestion in suggestions):
            suggestions.append(LegalSuggestion(
                name="Avenimiento",
                suggestion_type=SuggestionType.COMPROMISE,
                score=probable_stats.withdrawal_chance or 0.05,
            ))
        if not any(suggestion.suggestion_type == SuggestionType.WITHDRAWAL for suggestion in suggestions):
            suggestions.append(LegalSuggestion(
                name="Desistimiento",
                suggestion_type=SuggestionType.WITHDRAWAL,
                score=probable_stats.withdrawal_chance or 0.02,
            ))

        for suggestion in suggestions:
            if suggestion.suggestion_type == SuggestionType.COMPROMISE:
                input = CompromiseGeneratorInput(
                    suggestion=suggestion.description,
                    case_title=self.case.title,
                    case_role=court_case.role,
                    court_city=court_case.city,
                    court_number=court_case.number,
                    plaintiffs=plaintiffs,
                    sponsoring_attorneys=sponsoring_attorneys,
                    defendants=defendants,
                    defendant_attorneys=defendant_attorneys,
                    demand_text=demand_text,
                )
                generator = CompromiseGenerator(input)
                response = generator.generate()
                if structured_output := response.structured_output:
                    new_suggestion = CaseEventSuggestion(
                        case_event_id=event.id,
                        case_event=event,
                        name=suggestion.name or "Avenimiento",
                        content=structured_output.model_dump(),
                        type=suggestion.suggestion_type,
                        score=suggestion.score,
                    )
                    session.add(new_suggestion)
                    session.commit()
            
            elif suggestion.suggestion_type == SuggestionType.DEMAND_TEXT_CORRECTION:
                input = DemandTextCorrectionInput(
                    suggestion=suggestion.description,
                    case_title=self.case.title,
                    case_role=court_case.role,
                    court_city=court_case.city,
                    court_number=court_case.number,
                    attorneys=sponsoring_attorneys,
                )
                generator = DemandTextCorrectionGenerator(input)
                correction = generator.generate(information, demand_text)
                new_suggestion = CaseEventSuggestion(
                    case_event_id=event.id,
                    case_event=event,
                    name=suggestion.name or "Corrección",
                    content=correction.model_dump(),
                    type=suggestion.suggestion_type,
                    score=suggestion.score,
                )
                session.add(new_suggestion)
                session.commit()
            
            elif suggestion.suggestion_type == SuggestionType.RESPONSE:
                input = LegalResponseInput(
                    suggestion=suggestion.description,
                    case_title=self.case.title,
                    case_role=court_case.role,
                    court_city=court_case.city,
                    court_number=court_case.number,
                    attorneys=sponsoring_attorneys,
                    #TODO: Consider posibility of adding a request
                )
                generator = LegalResponseGenerator(input)
                response = generator.generate_from_dispatch_resolution(information, demand_text)
                new_suggestion = CaseEventSuggestion(
                    case_event_id=event.id,
                    case_event=event,
                    name=suggestion.name or "Respuesta",
                    content=response.model_dump(),
                    type=suggestion.suggestion_type,
                    score=suggestion.score,
                )
                session.add(new_suggestion)
                session.commit()
            
            elif suggestion.suggestion_type == SuggestionType.WITHDRAWAL:
                input = WithdrawalGeneratorInput(
                    suggestion=suggestion.description,
                    case_title=self.case.title,
                    case_role=court_case.role,
                    court_city=court_case.city,
                    court_number=court_case.number,
                    plaintiffs=plaintiffs,
                    sponsoring_attorneys=sponsoring_attorneys,
                    debtors=[d for d in defendants if d.type == DefendantType.DEBTOR],
                    co_debtors=[d for d in defendants if d.type == DefendantType.CO_DEBTOR],
                    legal_article="148 del Código de Procedimiento Civil"
                )
                generator = WithdrawalGenerator(input)
                response = generator.generate()
                if structured_output := response.structured_output:
                    new_suggestion = CaseEventSuggestion(
                        case_event_id=event.id,
                        case_event=event,
                        name=suggestion.name or "Desistimiento",
                        content=structured_output.model_dump(),
                        type=suggestion.suggestion_type,
                        score=suggestion.score,
                    )
                    session.add(new_suggestion)
                    session.commit()
        return suggestions

    def _process_information(
            self,
            session: Session,
            information: DispatchResolutionInformation,
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
        
        event = valid_case_events[-1]
        statement = select(CaseEvent).where(
            CaseEvent.case_id == self.case.id,
            CaseEvent.id == event.next_event_id,
        )
        next_event = session.exec(statement).first()
        if next_event:
            raise ValueError("Case does not have unresolved demand text events.")

        court_case_statement = select(CourtCase).where(
            CourtCase.case_id == self.case.id,
            CourtCase.simulated == self.case.simulated,
        )
        court_case = session.exec(court_case_statement).first()
        if not court_case:
            court_case = CourtCase(
                city=self.case.city,
                number=information.court_number,
                role=information.case_role,
                simulated=self.case.simulated,
                case_id=self.case.id,
                case=self.case,
            )
            if information.case_title:
                self.case.title = information.case_title

        try:
            self.case.status = CaseStatus.ACTIVE
            new_case_event = CaseEvent(
                id=uuid4(),
                case_id=self.case.id,
                case=self.case,
                title="Ordena despachar mandamiento",
                source=CaseParty.COURT,
                target=CaseParty.PLAINTIFFS,
                type=CaseEventType.DISPATCH_RESOLUTION,
                previous_event_id=event.id,
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
                    raise ValueError(f"Could not store dispatch resolution in S3: {e}")
            new_document = self._create_document("Resolución despáchese", new_case_event, key, structure)

            session.add(new_document)
            session.add(new_case_event)
            session.add(court_case)
            if next_event:
                session.delete(next_event)
            session.commit()
            event.next_event_id = new_case_event.id
            session.commit()
            return new_case_event
        except Exception as e:
            session.rollback()
            raise e
