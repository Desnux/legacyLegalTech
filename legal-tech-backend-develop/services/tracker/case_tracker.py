import logging
import random
from datetime import datetime, timedelta
from uuid import uuid4, UUID

from sqlmodel import delete, select

from database.ext_db import Session
from models.pydantic import (
    AnnexFile,
    AttachmentInformationExtended,
    Attorney,
    Defendant,
    DefendantType,
    DemandExceptionStructure,
    DispatchResolutionStructure,
    DocumentType,
    JudicialCollectionDemandExceptionInput,
    JudicialCollectionDispatchResolutionInput,
    LegalCompromise,
    LegalCompromiseInput,
    LegalResolution,
    LegalResolutionInput,
    LegalSubject,
    Plaintiff,
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
    Document,
    Litigant,
    LitigantRole,
)
from services.extractor import (
    LegalResolutionExtractor,
)
from services.generator import (
    DemandExceptionGenerator,
    DispatchResolutionGenerator,
    LegalResolutionGenerator,
)
from services.simulator import LitigantSimulator
from services.v2.document.demand_text import (
    DemandTextGeneratorInput,
    DemandTextStructure,
)
from services.v2.document.compromise import (
    CompromiseGenerator,
    CompromiseGeneratorInput,
    CompromiseStructure,
)
from storage.s3_storage import S3Storage


class CaseTracker:
    def __init__(self, case: Case | None = None) -> None:
        self.case: Case | None = case

    def create_case_from_demand_text(
            self,
            session: Session,
            information: DemandTextGeneratorInput,
            structure: DemandTextStructure,
            annexes: list[AnnexFile] = [],
            simulated: bool = False,
        ) -> Case:
        """Creates a case in the database given the information and structure of a demand text."""
        try:
            if not information.plaintiff:
                raise ValueError("Expected exactly 1 plaintiff.")
            if len(information.sponsoring_attorneys or []) == 0:
                raise ValueError("Expected at least 1 sponsoring attorney.")
            if information.defendants is None or len(information.defendants or []) == 0:
                raise ValueError("Expected at least 1 defendant.")
            highest_defendant = max(information.defendants, key=lambda d: d.get_numeric_identifier())
            
            new_case = Case(
                id=uuid4(),
                title=f"{information.plaintiff.name.upper()}/{highest_defendant.name.upper()}",
                city=information.city or "",
                legal_subject=information.legal_subject or LegalSubject.GENERAL_COLLECTION,
                winner=None,
                status=CaseStatus.DRAFT,
                amount=information.amount,
                amount_currency=information.amount_currency,
                simulated=simulated,
            )

            new_case_event = CaseEvent(
                id=uuid4(),
                case_id=new_case.id,
                case=new_case,
                title="Ingreso demanda",
                source=CaseParty.PLAINTIFFS,
                target=CaseParty.COURT,
                type=CaseEventType.DEMAND_START,
                simulated=simulated,
            )
            
            for attorney in information.sponsoring_attorneys or []:
                new_litigant = Litigant(
                    id=uuid4(),
                    name=attorney.name,
                    rut=attorney.identifier,
                    case_id=new_case.id,
                    case=new_case,
                    role=LitigantRole.SPONSORING_ATTORNEY,
                    simulated=simulated,
                )
                session.add(new_litigant)
            
            new_document = Document(
                name="Texto de demanda",
                type=DocumentType.DEMAND_TEXT,
                content=structure.model_dump(),
                case_event_id=new_case_event.id,
                case_event=new_case_event,
                generated=True,
                simulated=simulated,
            )

            plaintiff = Defendant(
                name=information.plaintiff.name,
                identifier=information.plaintiff.identifier,
                legal_representatives=information.legal_representatives,
            )
            self._add_litigants(session, [plaintiff], LitigantRole.PLAINTIFF, new_case, simulated)
            self._add_litigants(session, information.defendants or [], LitigantRole.DEFENDANT, new_case, simulated)

            s3 = S3Storage()
            for i, annex in enumerate(annexes):
                file_content = annex.upload_file.file.read()
                storage_key = f"case/{new_case.id}/event/{new_case_event.id}/annex_{i}.pdf"
                try:
                    s3.save(storage_key, file_content)
                except Exception as e:
                    logging.warning(f"Could not store annex in S3: {e}")
                    continue
                new_annex = Document(
                    name=annex.label,
                    type=DocumentType.OTHER,
                    storage_key=storage_key,
                    case_event_id=new_case_event.id,
                    case_event=new_case_event,
                    generated=False,
                    simulated=simulated,
                )
                session.add(new_annex)

            session.add(new_case)
            session.add(new_case_event)
            session.add(new_document)
            session.commit()
            session.refresh(new_case)
            self.case = new_case
            return new_case
        except Exception as e:
            session.rollback()
            raise e

    def create_legal_resolution_from_attachments(self, session: Session, attachments: list[AttachmentInformationExtended]) -> LegalResolution | None:
        if self.case is None:
            raise ValueError("No case is being tracked.")
        statement = (
            select(CaseEvent)
            .where(
                CaseEvent.case_id == self.case.id,
                CaseEvent.type == CaseEventType.EXCEPTIONS,
                CaseEvent.next_event_id == None,
                CaseEvent.simulated == False,
            )
            .order_by(CaseEvent.created_at)
        )
        valid_case_events = session.exec(statement).all()
        if len(valid_case_events) == 0:
            statement = (
                select(CaseEvent)
                .where(
                    CaseEvent.case_id == self.case.id,
                    CaseEvent.type == CaseEventType.EXCEPTIONS_RESPONSE,
                    CaseEvent.next_event_id == None,
                    CaseEvent.simulated == False,
                )
                .order_by(CaseEvent.created_at)
            )
            valid_case_events = session.exec(statement).all()
        if len(valid_case_events) == 0:
            raise ValueError("Case does not have uncontested non-simulated exception events.")
        event = valid_case_events[-1]
        
        legal_resolution_attachment = next(
            filter(lambda x: x.document_type == DocumentType.RESOLUTION, attachments),
            None,
        )
        if legal_resolution_attachment is None:
            raise ValueError("Could not find attachment that contains a legal resolution.")
        extractor = LegalResolutionExtractor()
        structure = extractor.extract_from_text(legal_resolution_attachment.content or "")
        if not structure:
            raise ValueError("Invalid legal resolution.")
        
        court_case_statement = select(CourtCase).where(CourtCase.case_id == self.case.id, CourtCase.simulated == False)
        court_case = session.exec(court_case_statement).first()
        if not court_case:
            raise ValueError("Case without a real court.")
        
        try:
            if self.case.status != CaseStatus.ACTIVE:
                self.case.status = CaseStatus.ACTIVE
                session.add(self.case)

            new_case_event = CaseEvent(
                id=uuid4(),
                case_id=self.case.id,
                case=self.case,
                title="Resolución",
                source=CaseParty.COURT,
                target=CaseParty.DEFENDANTS,
                type=CaseEventType.RESOLUTION,
                previous_event_id=event.id,
                simulated=False,
            )
            new_document = Document(
                name="Resolución",
                type=DocumentType.RESOLUTION,
                content=structure.model_dump(),
                case_event_id=new_case_event.id,
                case_event=new_case_event,
                storage_key=legal_resolution_attachment.key,
                generated=False,
                simulated=False,
            )
            session.add(new_document)
            session.add(new_case_event)
            session.add(court_case)
            session.commit()
            event.next_event_id = new_case_event.id
            session.commit()
            return structure
        except Exception as e:
            session.rollback()
            raise e

    def register_suggestion(self, session: Session, event: CaseEvent, suggestion: CaseEventSuggestion, simulated: bool) -> None:
        if self.case is None:
            logging.warning("No case is being tracked.")
            return None
        
        event_type = CaseEventType.OTHER
        document_type = DocumentType.OTHER
        document_name = "Escrito"
        match suggestion.type:
            case SuggestionType.DEMAND_TEXT_CORRECTION:
                event_type = CaseEventType.DEMAND_TEXT_CORRECTION
                document_type = DocumentType.DEMAND_TEXT_CORRECTION
                document_name = "Rectifica demanda"
            case SuggestionType.EXCEPTIONS_RESPONSE:
                event_type = CaseEventType.EXCEPTIONS_RESPONSE
                document_type = DocumentType.EXCEPTIONS_RESPONSE
                document_name = "Evacúa traslado"
            case SuggestionType.RESPONSE:
                event_type = CaseEventType.RESPONSE
                document_type = DocumentType.RESPONSE
                document_name = "Cumple lo ordenado"
            case SuggestionType.REQUEST:
                event_type = CaseEventType.REQUEST
                document_type = DocumentType.REQUEST
                document_name = "Solicita"
            case SuggestionType.COMPROMISE:
                event_type = CaseEventType.COMPROMISE
                document_type = DocumentType.COMPROMISE
                document_name = "Avenimiento"
        
        try:
            new_case_event = CaseEvent(
                id=uuid4(),
                case_id=self.case.id,
                case=self.case,
                title=document_name,
                source=CaseParty.PLAINTIFFS,
                target=event.source,
                type=event_type,
                previous_event_id=event.id,
                simulated=simulated,
            )
            new_document = Document(
                name=document_name,
                type=document_type,
                content=suggestion.content,
                case_event_id=new_case_event.id,
                case_event=new_case_event,
                generated=True,
                simulated=simulated,
            )
            session.add(new_document)
            session.add(new_case_event)
            #session.exec(
            #    delete(CaseEventSuggestion).where(CaseEventSuggestion.case_event_id == event.id)
            #)
            session.commit()
            event.next_event_id = new_case_event.id
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

    def simulate_demand_exception(self, session: Session, event: CaseEvent) -> DemandExceptionStructure | None:
        if self.case is None:
            logging.warning("No case is being tracked.")
            return None
        demand_text_structured = self._get_demand_text_structure(session, event)
        if demand_text_structured is None:
            return None
        
        court_case_statement = select(CourtCase).where(CourtCase.case_id == self.case.id)
        court_case = session.exec(court_case_statement).first()
        if not court_case:
            logging.warning("Case without a court.")
            return None

        plaintiff_attorneys_statement = select(Litigant).where(Litigant.case_id == self.case.id, Litigant.role == LitigantRole.SPONSORING_ATTORNEY)
        plaintiff_attorney_litigants = session.exec(plaintiff_attorneys_statement).all()
        plaintiff_attorneys = [
            Attorney(name=x.name, identifier=x.rut)
            for x in plaintiff_attorney_litigants
        ]
        
        plaintiffs_statement = select(Litigant).where(Litigant.case_id == self.case.id, Litigant.role == LitigantRole.PLAINTIFF)
        plaintiff_litigants = session.exec(plaintiffs_statement).all()
        plaintiffs = [
            Plaintiff(name=x.name, identifier=x.rut)
            for x in plaintiff_litigants
        ]

        defendants_statement = select(Litigant).where(Litigant.case_id == self.case.id, Litigant.role == LitigantRole.DEFENDANT)
        defendant_litigants = session.exec(defendants_statement).all()
        defendants = [
            Defendant(name=x.name, identifier=x.rut, address=x.address)
            for x in defendant_litigants
        ]

        # Get or simulate defendant attorneys
        defendant_attorneys_statement = select(Litigant).where(Litigant.case_id == self.case.id, Litigant.role == LitigantRole.DEFENDANT_ATTORNEY)
        defendant_attorney_litigants = session.exec(defendant_attorneys_statement).all()
        defendant_attorneys = [
            Attorney(name=x.name, identifier=x.rut)
            for x in defendant_attorney_litigants
        ]

        new_attorney = None
        if len(defendant_attorneys) == 0:
            simulated_attorney = LitigantSimulator.simulate_attorney()
            new_attorney = Litigant(
                id=uuid4(),
                name=simulated_attorney.name,
                rut=simulated_attorney.identifier,
                case_id=self.case.id,
                case=self.case,
                role=LitigantRole.DEFENDANT_ATTORNEY,
                simulated=True,
            )
            defendant_attorneys = [simulated_attorney]
        
        # Simulate input for demand exceptions
        input = JudicialCollectionDemandExceptionInput(
            court_city=court_case.city,
            court_number=court_case.number,
            case_role=court_case.role,
            case_title=self.case.title,
            plaintiffs=plaintiffs,
            plaintiff_attorneys=plaintiff_attorneys,
            defendants=defendants,
            defendant_attorneys=defendant_attorneys,
            demand_text_date=event.created_at.date(),
        )
        demand_exception_generator = DemandExceptionGenerator(input)
        demand_exception = demand_exception_generator.simulate_from_structured(demand_text_structured)

        # Save to database
        try:
            new_case_event = CaseEvent(
                id=uuid4(),
                case_id=self.case.id,
                case=self.case,
                title="Opone excepciones",
                source=CaseParty.DEFENDANTS,
                target=CaseParty.PLAINTIFFS,
                type=CaseEventType.EXCEPTIONS,
                simulated=True,
            )
            new_document = Document(
                name="Opone excepciones",
                type=DocumentType.EXCEPTIONS,
                content=demand_exception.model_dump(),
                case_event_id=new_case_event.id,
                case_event=new_case_event,
                generated=True,
                simulated=True,
            )
            if new_attorney:
                session.add(new_attorney)
            session.add(new_document)
            session.add(new_case_event)
            session.commit()
            return demand_exception
        except Exception as e:
            session.rollback()
            raise e

    def simulate_dispatch_resolution(self, session: Session, event: CaseEvent) -> DispatchResolutionStructure | None:
        if self.case is None:
            logging.warning("No case is being tracked.")
            return None
        demand_text_structured = self._get_demand_text_structure(session, event)
        if demand_text_structured is None:
            return None

        local_random = random.Random()
        court_case_statement = select(CourtCase).where(CourtCase.case_id == self.case.id)
        court_case = session.exec(court_case_statement).first()
        if not court_case:
            court_case = CourtCase(
                city=self.case.city,
                number=local_random.randint(1, 10),
                role=f"C-{local_random.randint(100, 9999)}-{event.created_at.year}",
                simulated=True,
                case_id=self.case.id,
                case=self.case,
            )
        
        input = JudicialCollectionDispatchResolutionInput(
            court_city=court_case.city,
            court_number=court_case.number,
            case_role=court_case.role,
            case_title=self.case.title,
            issue_date=datetime.now().date(),
            demand_text_date=event.created_at.date(),
        )
        dispatch_resolution_generator = DispatchResolutionGenerator(input)
        dispatch_resolution = dispatch_resolution_generator.simulate_from_structured(demand_text_structured)

        try:
            new_case_event = CaseEvent(
                id=uuid4(),
                case_id=self.case.id,
                case=self.case,
                title="Ordena despachar mandamiento",
                source=CaseParty.COURT,
                target=CaseParty.PLAINTIFFS,
                type=CaseEventType.DISPATCH_RESOLUTION,
                previous_event_id=event.id,
                simulated=True,
            )
            new_document = Document(
                name="Resolución despáchese",
                type=DocumentType.DISPATCH_RESOLUTION,
                content=dispatch_resolution.model_dump(),
                case_event_id=new_case_event.id,
                case_event=new_case_event,
                generated=True,
                simulated=True,
            )
            session.add(new_document)
            session.add(new_case_event)
            session.add(court_case)
            session.commit()
            event.next_event_id = new_case_event.id
            session.commit()
            return dispatch_resolution
        except Exception as e:
            session.rollback()
            raise e

    def simulate_legal_compromise(self, session: Session, include_simulated_data: bool) -> CompromiseStructure | None:
        if self.case is None:
            logging.warning("No case is being tracked.")
            return None
        demand_text_structured = self._get_demand_text_structure(session)
        if demand_text_structured is None:
            return None
        court_case_statement = select(CourtCase).where(CourtCase.case_id == self.case.id, True if include_simulated_data else CourtCase.simulated == False)
        court_case = session.exec(court_case_statement).first()
        if not court_case:
            raise ValueError("Case without a real court.")
        plaintiffs = self._get_plaintiffs(session, include_simulated_data)
        sponsoring_attorneys = self._get_sponsoring_attorneys(session, include_simulated_data)
        defendants = self._get_defendants(session, include_simulated_data)
        defendant_attorneys = self._get_defendant_attorneys(session, include_simulated_data)
        
        input = CompromiseGeneratorInput(
            suggestion=None,
            demand_text=demand_text_structured,
            case_title=self.case.title,
            case_role=court_case.role,
            court_city=court_case.city,
            court_number=court_case.number,
            plaintiffs=plaintiffs,
            sponsoring_attorneys=sponsoring_attorneys,
            defendants=defendants,
            defendant_attorneys=defendant_attorneys,
        )
        generator = CompromiseGenerator(input)
        try:
            compromise = generator.generate()
        except Exception as e:
            logging.warning(f"Could not generate legal compromise: {e}")
            return None
        return compromise.structured_output
    
    def simulate_legal_resolution(self, session: Session, event: CaseEvent) -> LegalResolution | None:
        if self.case is None:
            logging.warning("No case is being tracked.")
            return None
        demand_exception_structured = self._get_demand_exception_structure(session, event)
        if demand_exception_structured is None:
            return None

        local_random = random.Random()
        has_hearing = True #TODO: Adapt
        court_case_statement = select(CourtCase).where(CourtCase.case_id == self.case.id)
        court_case = session.exec(court_case_statement).first()
        if not court_case:
            logging.warning("Case without a court.")
            return None
        
        if has_hearing:
            if random.choice([True, False]):
                hearing_days = [random.randint(2, 9)]
            else:
                start = random.randint(2, 8)
                hearing_days = [start, start + 1]
        else:
            hearing_days = None
        input = LegalResolutionInput(
            court_city=court_case.city,
            court_number=court_case.number,
            case_role=court_case.role,
            case_title=self.case.title,
            issue_date=datetime.now().date(),
            hearing_days=hearing_days,
            hearing_hour=f"{local_random.randint(8, 12):02d}:00" if has_hearing else None,
            demand_text_date=event.created_at.date(),
        )
        legal_resolution_generator = LegalResolutionGenerator(input)
        legal_resolution = legal_resolution_generator.generate_from_demand_exception(demand_exception_structured)

        try:
            new_case_event = CaseEvent(
                id=uuid4(),
                case_id=self.case.id,
                case=self.case,
                title="Resolución",
                source=CaseParty.COURT,
                target=CaseParty.DEFENDANTS,
                type=CaseEventType.RESOLUTION,
                previous_event_id=event.id,
                simulated=True,
            )
            new_document = Document(
                name="Resolución",
                type=DocumentType.DISPATCH_RESOLUTION,
                content=legal_resolution.model_dump(),
                case_event_id=new_case_event.id,
                case_event=new_case_event,
                generated=True,
                simulated=True,
            )
            session.add(new_document)
            session.add(new_case_event)
            session.add(court_case)
            session.commit()
            event.next_event_id = new_case_event.id
            session.commit()
            return legal_resolution
        except Exception as e:
            session.rollback()
            raise e

    def simulate_future_events(self, session: Session) -> None:
        event_0 = CaseEvent(
            id=UUID("b223d133-0daf-41b6-a791-c9ce280a99e0"),
            case_id=self.case.id,
            case=self.case,
            title="Citación para oír sentencia",
            source=CaseParty.COURT,
            target=CaseParty.DEFENDANTS,
            type=CaseEventType.RESOLUTION,
            simulated=True,
            created_at=datetime.now() + timedelta(hours=2),
        )
        document_0 = Document(
            id=UUID("b223d133-0daf-41b6-b802-c9ce280a99e0"),
            name="Citación para oír sentencia",
            type=DocumentType.RESOLUTION,
            content=None,
            case_event_id=event_0.id,
            generated=True,
            simulated=True,
        )
        event_1 = CaseEvent(
            id=UUID("b223d133-0daf-41b6-a791-c9ce280a99e1"),
            case_id=self.case.id,
            case=self.case,
            title="Sentencia definitiva",
            source=CaseParty.COURT,
            target=CaseParty.DEFENDANTS,
            type=CaseEventType.RESOLUTION,
            simulated=True,
            created_at=datetime.now() + timedelta(days=2, hours=4, minutes=15),
        )
        document_1 = Document(
            id=UUID("b223d133-0daf-41b6-b802-c9ce280a99e1"),
            name="Sentencia definitiva",
            type=DocumentType.RESOLUTION,
            content=None,
            case_event_id=event_1.id,
            generated=True,
            simulated=True,
        )
        event_2 = CaseEvent(
            id=UUID("b223d133-0daf-41b6-a791-c9ce280a99e2"),
            case_id=self.case.id,
            case=self.case,
            title="Mandamiento de ejecución y embargo",
            source=CaseParty.COURT,
            target=CaseParty.DEFENDANTS,
            type=CaseEventType.RESOLUTION,
            simulated=True,
            created_at=datetime.now() + timedelta(days=3, hours=1, minutes=8),
        )
        document_2 = Document(
            id=UUID("b223d133-0daf-41b6-b802-c9ce280a99e2"),
            name="Mandamiento de ejecución y embargo",
            type=DocumentType.RESOLUTION,
            content=None,
            case_event_id=event_2.id,
            generated=True,
            simulated=True,
        )
        event_3 = CaseEvent(
            id=UUID("b223d133-0daf-41b6-a791-c9ce280a99e3"),
            case_id=self.case.id,
            case=self.case,
            title="Tercería de dominio",
            source=CaseParty.EXTERNAL_PARTY,
            target=CaseParty.COURT,
            type=CaseEventType.REQUEST,
            simulated=True,
            created_at=datetime.now() + timedelta(days=37, hours=2, minutes=47),
        )
        document_3 = Document(
            id=UUID("b223d133-0daf-41b6-b802-c9ce280a99e3"),
            name="Tercería de dominio",
            type=DocumentType.REQUEST,
            content=None,
            case_event_id=event_3.id,
            generated=True,
            simulated=True,
        )
        events = [event_0, event_1, event_2, event_3]
        documents = [document_0, document_1, document_2, document_3]
        try:
            for i in range(len(events)):
                statement = (
                    select(CaseEvent)
                    .where(CaseEvent.case_id == self.case.id, CaseEvent.id == events[i].id)
                )
                valid_event = session.exec(statement).first()
                if not valid_event:
                    session.add(events[i])
                    session.add(documents[i])
                    session.commit()
                    if i == 0:
                        statement = (
                            select(CaseEvent)
                            .where(CaseEvent.case_id == self.case.id, CaseEvent.title == "Ordena despachar mandamiento")
                        )
                        court_event = session.exec(statement).first()
                        statement = (
                            select(CaseEvent)
                            .where(CaseEvent.case_id == self.case.id, CaseEvent.title == "Opone excepciones")
                        )
                        exceptions_event = session.exec(statement).first()
                        if exceptions_event and court_event:
                            court_event.next_event_id = exceptions_event.id
                            court_event.previous_event_id = court_event.id
                            session.commit()
                    if i > 0:
                        if i != len(events) - 1:
                            events[i - 1].next_event_id = events[i].id
                            events[i].previous_event_id = events[i - 1].id
                        self.case.winner = CaseParty.PLAINTIFFS
                        session.commit()
                    break
            else:
                logging.info("All future events are in the database")
        except Exception as e:
            session.rollback()
            raise e
    
    def clear_future_events(self, session: Session) -> None:
        ids_to_delete = [
            "b223d133-0daf-41b6-a791-c9ce280a99e0",
            "b223d133-0daf-41b6-a791-c9ce280a99e1",
            "b223d133-0daf-41b6-a791-c9ce280a99e2",
            "b223d133-0daf-41b6-a791-c9ce280a99e3",
        ]
        try:
            session.exec(delete(CaseEvent).where(CaseEvent.id.in_(ids_to_delete)))
            self.case.winner = None
            statement = (
                select(CaseEvent)
                .where(CaseEvent.case_id == self.case.id, CaseEvent.title == "Opone excepciones")
            )
            exceptions_event = session.exec(statement).first()
            if exceptions_event:
                exceptions_event.previous_event_id = None
            statement = (
                select(CaseEvent)
                .where(CaseEvent.case_id == self.case.id, CaseEvent.title == "Ordena despachar mandamiento")
            )
            court_event = session.exec(statement).first()
            if court_event:
                court_event.next_event_id = None
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

    def _add_litigants(self, session: Session, litigants: list[Defendant], role: LitigantRole, case: Case, simulated: bool) -> None:
        for litigant in litigants:
            new_litigant = Litigant(
                id=uuid4(),
                address=litigant.address if litigant.address else None,
                name=litigant.name,
                rut=litigant.identifier,
                case_id=case.id,
                case=case,
                role=role,
                simulated=simulated,
                is_co_debtor=litigant.type == DefendantType.CO_DEBTOR and role == LitigantRole.DEFENDANT,
            )
            for legal_rep in litigant.legal_representatives or []:
                new_sub_litigant = Litigant(
                    name=legal_rep.name,
                    rut=legal_rep.identifier,
                    case_id=case.id,
                    case=case,
                    role=LitigantRole.LEGAL_REPRESENTATIVE,
                    represented_litigant_id=new_litigant.id,
                    represented_litigant=new_litigant,
                    simulated=simulated,
                )
                session.add(new_sub_litigant)
            session.add(new_litigant)

    def _get_defendant_attorneys(self, session: Session, include_simulated: bool) -> list[Attorney]:
        statement = select(Litigant).where(
            Litigant.case_id == self.case.id,
            (Litigant.simulated == False) if not include_simulated else True,
            Litigant.role == LitigantRole.DEFENDANT_ATTORNEY,
        )
        result = session.exec(statement).all()
        return [Attorney(name=litigant.name, identifier=litigant.rut, address=litigant.address) for litigant in result]

    def _get_defendants(self, session: Session, include_simulated: bool) -> list[Defendant]:
        statement = select(Litigant).where(
            Litigant.case_id == self.case.id,
            (Litigant.simulated == False) if not include_simulated else True,
            Litigant.role == LitigantRole.DEFENDANT,
        )
        result = session.exec(statement).all()
        return [Defendant(name=litigant.name, identifier=litigant.rut, address=litigant.address) for litigant in result]

    def _get_demand_exception_structure(self, session: Session, event: CaseEvent | None = None) -> DemandExceptionStructure | None:
        if not event:
            statement = (
                select(CaseEvent)
                .where(CaseEvent.case_id == self.case.id, CaseEvent.type == CaseEventType.EXCEPTIONS, CaseEvent.simulated == False)
                .order_by(CaseEvent.created_at)
            )
            event = session.exec(statement).first()
        if not event:
            return None
        statement = (
            select(Document)
            .where(Document.case_event_id == event.id, Document.type == DocumentType.EXCEPTIONS)
        )
        demand_exception = session.exec(statement).first()
        if not demand_exception:
            logging.warning("No demand exception in case event.")
            return None
        if demand_exception.content is None:
            logging.warning("Demand exception without content.")
            return None
        return DemandExceptionStructure(**demand_exception.content)

    def _get_demand_text_structure(self, session: Session, event: CaseEvent | None = None) -> DemandTextStructure | None:
        if not event:
            statement = (
                select(CaseEvent)
                .where(CaseEvent.case_id == self.case.id, CaseEvent.type == CaseEventType.DEMAND_START, CaseEvent.simulated == False)
                .order_by(CaseEvent.created_at)
            )
            event = session.exec(statement).first()
        if not event:
            return None
        statement = (
            select(Document)
            .where(Document.case_event_id == event.id, Document.type == DocumentType.DEMAND_TEXT)
        )
        demand_text = session.exec(statement).first()
        if not demand_text:
            logging.warning("No demand text in case event.")
            return None
        if demand_text.content is None:
            logging.warning("Demand text without content.")
            return None
        return DemandTextStructure(**demand_text.content)

    def _get_plaintiffs(self, session: Session, include_simulated: bool) -> list[Plaintiff]:
        statement = select(Litigant).where(
            Litigant.case_id == self.case.id,
            (Litigant.simulated == False) if not include_simulated else True,
            Litigant.role == LitigantRole.PLAINTIFF,
        )
        result = session.exec(statement).all()
        return [Plaintiff(name=litigant.name, identifier=litigant.rut) for litigant in result]
    
    def _get_sponsoring_attorneys(self, session: Session, include_simulated: bool) -> list[Attorney]:
        statement = select(Litigant).where(
            Litigant.case_id == self.case.id,
            (Litigant.simulated == False) if not include_simulated else True,
            Litigant.role == LitigantRole.SPONSORING_ATTORNEY,
        )
        result = session.exec(statement).all()
        return [Attorney(name=litigant.name, identifier=litigant.rut, address=litigant.address) for litigant in result]
