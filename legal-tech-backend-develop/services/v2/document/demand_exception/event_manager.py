import random
from datetime import datetime, date
from sqlmodel import select
from uuid import uuid4

from database.ext_db import Session
from models.pydantic import (
    Attorney,
    DefendantType,
    DemandExceptionStructure,
    DocumentType,
    LegalExceptionResponseInput,
    LegalSuggestion,
    SuggestionType,
)
from models.sql import (
    Case,
    CaseEvent,
    CaseEventSuggestion,
    CaseEventType,
    CaseParty,
    CourtCase,
    Litigant,
    LitigantRole,
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
from .extractor import DemandExceptionExtractor
from .models import (
    DemandExceptionInformation,
    DemandExceptionExtractorInput,
    DemandExceptionExtractorOutput,
)
from .suggester import DemandExceptionSuggester


class DemandExceptionEventManager(
    GenericEventManager[
        DemandExceptionStructure,
        DemandExceptionExtractorInput,
        DemandExceptionInformation,
        DemandExceptionExtractorOutput,
        DemandTextStructure,
    ]
):
    """Demand exception event manager."""

    def __init__(self, case: Case) -> None:
        super().__init__(case, DocumentType.EXCEPTIONS, DemandExceptionExtractor, DemandExceptionExtractorInput, DemandTextStructure)

    def _create_suggestions(
            self,
            session: Session,
            event: CaseEvent,
            information: DemandExceptionInformation,
            demand_text: DemandTextStructure,
        )-> list[LegalSuggestion] | None:
        court_case_statement = select(CourtCase).where(
            CourtCase.case_id == self.case.id,
            CourtCase.simulated == self.case.simulated,
        )
        from services.generator import DemandExceptionResponseGenerator
        court_case = session.exec(court_case_statement).first()
        if not court_case:
            raise ValueError("Case without a valid court.")
        plaintiffs = self._get_plaintiffs(session)
        sponsoring_attorneys = self._get_sponsoring_attorneys(session)
        defendants = self._get_defendants(session)
        defendant_attorneys = self._get_defendant_attorneys(session)
        
        suggester = DemandExceptionSuggester()
        suggestions = suggester.generate_suggestions_from_structure(information, demand_text)
        if not suggestions:
           suggestions = []
        
        probable_stats = self._get_probable_stats(session)
        if not any(suggestion.suggestion_type == SuggestionType.COMPROMISE for suggestion in suggestions):
            suggestions.append(LegalSuggestion(
                name="Avenimiento",
                suggestion_type=SuggestionType.COMPROMISE,
                score=probable_stats.compromise_chance or 0.10,
            ))
        if not any(suggestion.suggestion_type == SuggestionType.WITHDRAWAL for suggestion in suggestions):
            suggestions.append(LegalSuggestion(
                name="Desistimiento",
                suggestion_type=SuggestionType.WITHDRAWAL,
                score=probable_stats.withdrawal_chance or 0.05,
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

            elif suggestion.suggestion_type == SuggestionType.EXCEPTIONS_RESPONSE:
                input = LegalExceptionResponseInput(
                    suggestion=suggestion.description,
                    case_title=self.case.title,
                    case_role=court_case.role,
                    court_city=court_case.city,
                    court_number=court_case.number,
                    plaintiffs=plaintiffs,
                    sponsoring_attorneys=sponsoring_attorneys,
                    defendants=defendants,
                    defendant_attorneys=defendant_attorneys,
                )
                generator = DemandExceptionResponseGenerator(input)
                response = generator.generate(information, demand_text)
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
                    legal_article="467 del Código de Procedimiento Civil"
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
            information: DemandExceptionInformation,
            *,
            file_path: str | None = None,
            key: str | None = None,
            structure: DemandExceptionStructure | None = None,
            procedure_date: date | None = None,
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
        if not next_event:
            raise ValueError("Case does not have resolved demand text events.")

        court_case_statement = select(CourtCase).where(
            CourtCase.case_id == self.case.id,
            CourtCase.simulated == self.case.simulated,
        )
        court_case = session.exec(court_case_statement).first()
        if not court_case:
            if not information.court_city:
                raise ValueError("Case without a valid court and no court information found in the exception document.")
            
            court_case = CourtCase(
                city=information.court_city,
                number=information.court_number,
                role=information.case_role or f"C-{random.randint(100, 9999)}-{datetime.now().year}",
                simulated=self.case.simulated,
                case_id=self.case.id,
                case=self.case,
            )
            session.add(court_case)
            session.commit()
            session.refresh(court_case)
        
        defendant_attorneys_statement = select(Litigant).where(
            Litigant.case_id == self.case.id,
            Litigant.role == LitigantRole.DEFENDANT_ATTORNEY,
            Litigant.simulated == self.case.simulated,
        )
        defendant_attorney_litigants = session.exec(defendant_attorneys_statement).all()
        defendant_attorneys = [
            Attorney(name=x.name, identifier=x.rut)
            for x in defendant_attorney_litigants
        ]

        possible_new_attorneys: list[Attorney] = information.attorneys or []
        new_attorneys: list[Litigant] = []
        for attorney in possible_new_attorneys:
            attorney_name = attorney.name or ""
            attorney_identifier = attorney.identifier or ""
            include_attorney = True
            for previous_attorney in defendant_attorneys:
                if attorney_name.lower() == (previous_attorney.name or "").lower():
                    include_attorney = False
                if attorney_identifier.lower() == (previous_attorney.identifier or "").lower():
                    include_attorney = False
            if include_attorney:
                new_attorneys.append(Litigant(
                    id=uuid4(),
                    name=attorney_name,
                    rut=attorney_identifier,
                    case_id=self.case.id,
                    case=self.case,
                    role=LitigantRole.DEFENDANT_ATTORNEY,
                    simulated=self.case.simulated,
                ))

        try:
            new_case_event = CaseEvent(
                id=uuid4(),
                case_id=self.case.id,
                case=self.case,
                title="Opone excepciones",
                source=CaseParty.DEFENDANTS,
                target=CaseParty.PLAINTIFFS,
                type=CaseEventType.EXCEPTIONS,
                simulated=self.case.simulated,
                procedure_date=procedure_date,
            )

            if file_path and not key:   
                s3 = S3Storage()
                with open(file_path, "rb") as f:
                    file_content = f.read()
                key = f"case/{self.case.id}/event/{new_case_event.id}/annex_0.pdf"
                try:
                    s3.save(key, file_content)
                except Exception as e:
                    raise ValueError(f"Could not store demand exception in S3: {e}")
            new_document = self._create_document("Opone excepciones", new_case_event, key, structure)

            for new_attorney in new_attorneys:
                session.add(new_attorney)
            session.add(new_document)
            session.add(new_case_event)
            session.commit()
            return new_case_event
        except Exception as e:
            session.rollback()
            raise e
