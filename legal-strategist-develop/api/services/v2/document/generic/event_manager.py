import logging
from pydantic import BaseModel
from sqlmodel import select
from typing import Generic, Type, TypeVar

from database.ext_db import Session
from models.pydantic import (
    AttachmentInformationExtended,
    Attorney,
    Defendant,
    DefendantType,
    DocumentType,
    LegalSuggestion,
    Plaintiff,
    ProbableCaseStats,
)
from models.sql import (
    Case,
    CaseEvent,
    CaseEventType,
    Document,
    Litigant,
    LitigantRole,
)
from services.information import Statistics
from services.v2.document.base import (
    BaseEventManager,
    ExtractorInputBaseModel,
    InformationBaseModel,
    OutputBaseModel,
)
from .extractor import GenericExtractor


InformationType = TypeVar("InformationType", bound=InformationBaseModel)
StructureType = TypeVar("StructureType", bound=BaseModel)
InputType = TypeVar("InputType", bound=ExtractorInputBaseModel)
OutputType = TypeVar("OutputType", bound=OutputBaseModel[InformationType])
DemandType = TypeVar("DemandType", bound=InformationBaseModel)


class GenericEventManager(BaseEventManager, Generic[StructureType, InputType, InformationType, OutputType, DemandType]):
    """Generic event manager to handle different document types."""
    
    def __init__(
            self,
            case: Case,
            document_type: DocumentType,
            extractor: Type[GenericExtractor[InputType, InformationType, OutputType]],
            input_model: Type[InputType],
            demand_model: Type[DemandType]
        ) -> None:
        super().__init__(case)
        self.document_type = document_type
        self.extractor = extractor
        self.input_model = input_model
        self.demand_model = demand_model
    
    def create_from_attachments(
            self, 
            session: Session, 
            attachments: list[AttachmentInformationExtended]
        ) -> tuple[InformationType, CaseEvent]:
        attachment = next(
            filter(lambda x: x.document_type == self.document_type, attachments),
            None,
        )
        if attachment is None:
            raise ValueError("Could not find attachment that contains the required document type.")
        extractor_input = self.input_model(content=attachment.content)
        extractor = self.extractor(extractor_input)
        information = extractor.extract()
        if not information.structured_output:
            raise ValueError("Invalid attachment.")
        new_event = self._process_information(session, information.structured_output, key=attachment.key)
        return information.structured_output, new_event

    def create_from_file_path(
            self,
            session: Session,
            file_path: str
        ) -> tuple[InformationType, CaseEvent]:
        extractor_input = self.input_model(file_path=file_path)
        extractor = self.extractor(extractor_input)
        information = extractor.extract()
        if not information.structured_output:
            raise ValueError("Invalid file.")
        new_event = self._process_information(session, information.structured_output, file_path=file_path)
        return information.structured_output, new_event
    
    def create_suggestions(
            self,
            session: Session,
            event: CaseEvent,
            information: InformationType,
        ) -> list[LegalSuggestion] | None:
        demand_text = self._get_demand_text_structure(session)
        if demand_text is None:
            return None
        return self._create_suggestions(session, event, information, demand_text)
    
    def _create_document(
            self,
            name: str,
            event: CaseEvent,
            key: str | None,
            structure: StructureType | None,
        ) -> Document:
        document = Document(
            name=name,
            type=self.document_type,
            content=structure.model_dump() if structure else None,
            case_event_id=event.id,
            case_event=event,
            storage_key=key,
            generated=False if key else True,
            simulated=self.case.simulated,
        )
        return document
    
    def _create_suggestions(
            self,
            session: Session,
            event: CaseEvent,
            information: InformationType,
            demand_text: DemandType,
        )-> list[LegalSuggestion] | None:
        """Method to be overridden by subclasses to customize prompt."""
        raise NotImplementedError("Subclasses must implement _create_suggestions")
    
    def _get_demand_text_structure(self, session: Session, event: CaseEvent | None = None) -> DemandType | None:
        if not event:
            statement = (
                select(CaseEvent)
                .where(
                    CaseEvent.case_id == self.case.id,
                    CaseEvent.type == CaseEventType.DEMAND_START,
                    CaseEvent.simulated == self.case.simulated,
                )
                .order_by(CaseEvent.created_at)
            )
            event = session.exec(statement).first()
        if not event:
            return None
        statement = (
            select(Document)
            .where(
                Document.case_event_id == event.id,
                Document.type == DocumentType.DEMAND_TEXT,
            )
        )
        demand_text = session.exec(statement).first()
        if not demand_text:
            logging.warning("No demand text in case event.")
            return None
        if demand_text.content is None:
            logging.warning("Demand text without content.")
            return None
        return self.demand_model(**demand_text.content)
    
    def _get_defendant_attorneys(self, session: Session) -> list[Attorney]:
        statement = select(Litigant).where(
            Litigant.case_id == self.case.id,
            Litigant.simulated == self.case.simulated,
            Litigant.role == LitigantRole.DEFENDANT_ATTORNEY,
        )
        result = session.exec(statement).all()
        return [Attorney(name=litigant.name, identifier=litigant.rut, address=litigant.address) for litigant in result]

    def _get_defendants(self, session: Session) -> list[Defendant]:
        statement = select(Litigant).where(
            Litigant.case_id == self.case.id,
            Litigant.simulated == self.case.simulated,
            Litigant.role == LitigantRole.DEFENDANT,
        )
        result = session.exec(statement).all()
        return [
            Defendant(
                name=litigant.name,
                identifier=litigant.rut,
                address=litigant.address,
                type=DefendantType.CO_DEBTOR if litigant.is_co_debtor else DefendantType.DEBTOR,
            )
            for litigant in result
        ]

    def _get_plaintiffs(self, session: Session) -> list[Plaintiff]:
        statement = select(Litigant).where(
            Litigant.case_id == self.case.id,
            Litigant.simulated == self.case.simulated,
            Litigant.role == LitigantRole.PLAINTIFF,
        )
        result = session.exec(statement).all()
        return [Plaintiff(name=litigant.name, identifier=litigant.rut) for litigant in result]
    
    def _get_sponsoring_attorneys(self, session: Session) -> list[Attorney]:
        statement = select(Litigant).where(
            Litigant.case_id == self.case.id,
            Litigant.simulated == self.case.simulated,
            Litigant.role == LitigantRole.SPONSORING_ATTORNEY,
        )
        result = session.exec(statement).all()
        return [Attorney(name=litigant.name, identifier=litigant.rut, address=litigant.address) for litigant in result]
    
    def _get_probable_stats(self, session: Session) -> ProbableCaseStats:
        try:
            probable_stats = Statistics().get_probable_case_stats(session, self.case)
        except Exception as e:
            probable_stats = None
        if not probable_stats:
            logging.warning("Could not get probable stats for case")
            return ProbableCaseStats()
        logging.info(f"Probable stats: {probable_stats.model_dump()}")
        return probable_stats
        
    def _process_information(
            self,
            session: Session,
            information: InformationType,
            *,
            file_path: str | None = None,
            key: str | None = None,
            structure: StructureType | None = None,
        ) -> CaseEvent:
        """Method to be overridden by subclasses to customize prompt."""
        raise NotImplementedError("Subclasses must implement _process_information")
