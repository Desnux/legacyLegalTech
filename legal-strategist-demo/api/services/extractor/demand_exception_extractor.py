import logging

from pydantic import BaseModel, Field

from models.pydantic import Attorney, DemandExceptionStructure, JudicialCollectionDemandExceptionRequest
from services.extractor.base_extractor import BaseExtractor
from services.loader import PdfLoader


class DefendantAttorneys(BaseModel):
    attorneys: list[Attorney] | None = Field(None, description="List of attorney information")


class Exceptions(BaseModel):
    exceptions: list[JudicialCollectionDemandExceptionRequest] | None = Field(None, description="List of raised exceptions")


class Structure(BaseModel):
    header: str | None = Field(None, description="Header, indicates case role as well as court information, may be None")
    summary: str | None = Field(None, description="Summary, indicates main and additional requests as short statements")
    court: str | None = Field(None, description="Single line that describes the relevant court, may be S.J.L or also mention court number and city")
    opening: str | None = Field(None, description="Opening statement, includes mention of article 464, before listing each exception")
    exceptions: str | None = Field(None, description="Demand exceptions")
    main_request: str | None = Field(None, description="Main request after the exceptions")
    additional_requests: str | None = Field(None, description="Additional requests, also called Otrosí")


class DemandExceptionExtractor(BaseExtractor):
    def __init__(self) -> None:
        self.attorney_extractor = self.get_structured_extractor(DefendantAttorneys)
        self.exceptions_extractor = self.get_structured_extractor(Exceptions)
        self.structure_extractor = self.get_structured_extractor(Structure)
    
    def extract_attorney_information(self, text: str) -> list[Attorney] | None:
        if not text:
            logging.warning("Could not extract attorneys from empty text")
            return None
        try:
            attorney_info: DefendantAttorneys = self.attorney_extractor.invoke(self._get_prompt_attorney(text))
        except Exception as e:
            logging.warning(f"Could not extract attorneys from demand exception: {e}")
            return None
        return attorney_info.attorneys

    def extract_exceptions(self, text: str) -> list[JudicialCollectionDemandExceptionRequest] | None:
        if not text:
            logging.warning("Could not extract exceptions from empty text")
            return None
        try:
            exceptions: Exceptions = self.exceptions_extractor.invoke(self._get_prompt_exceptions(text))
        except Exception as e:
            logging.warning(f"Could not extract exceptions from demand exception: {e}")
            return None
        return exceptions.exceptions

    def extract_from_file_path(self, file_path: str) -> DemandExceptionStructure | None:
        loader = PdfLoader(file_path)
        documents = loader.load()
        if len(documents) == 0:
            return None
        full_text = "\n\n".join([document.page_content for document in documents])
        return self.extract_from_text(full_text)

    def extract_from_text(self, text: str) -> DemandExceptionStructure | None:
        if not text:
            logging.warning("Could not extract structure from empty demand exception")
            return None
        try:
            structure: Structure = self.structure_extractor.invoke(self._get_prompt_structure(text))
        except Exception as e:
            logging.warning(f"Could not extract structure from demand exception: {e}")
            return None
        return DemandExceptionStructure(**structure.model_dump(exclude={"court"}))
    
    def _get_prompt_attorney(self, content: str) -> str:
        prompt = f"""
        Consider the following content:
        <content>{content}</content>
        Extract information about the defendant attorneys.
        """
        return prompt
    
    def _get_prompt_exceptions(self, content: str) -> str:
        prompt = f"""
        Consider the following text of exceptions raised by defendants in a legal case:
        <content>{content}</content>
        Extract each exception listed given its nature and context.

        When answering, for every exception:
        - Use a valid legal exception nature value.
        - As context, consider the text related to each one, as literally as possible, in es_ES.
        """
        return prompt

    def _get_prompt_structure(self, content: str) -> str:
        prompt = f"""
        Consider the following dispatch resolution content from a file:
        <content>{content}</content>
        Output the same content in es_ES structured by section.
        Fix possible OCR errors by mending incomplete words and removing incorrect diacritics as well as noise.
        Ignore meta information, such as page numbers and digital signatures.
        """
        return prompt
