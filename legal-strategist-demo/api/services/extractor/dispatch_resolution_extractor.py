import logging

from pydantic import BaseModel, Field

from models.pydantic import CourtInformation, DispatchResolutionStructure
from services.extractor.base_extractor import BaseExtractor
from services.loader import PdfLoader


class Structure(BaseModel):
    header: str | None = Field(None, description="Dispatch resolution header, indicates case role as well as court information")
    date_line: str | None = Field(None, description="Dispatch resolution date line, includes city followed by human readable date")
    resolution: str | None = Field(None, description="Court resolution, includes main resolution as well as secondary or additional resolutions")
    footer: str | None = Field(None, description="Dispatch resolution footer, includes city followed by human readable date")


class DispatchResolutionExtractor(BaseExtractor):
    def __init__(self) -> None:
        self.court_extractor = self.get_structured_extractor(CourtInformation)
        self.structure_extractor = self.get_structured_extractor(Structure)
    
    def extract_court_information(self, text: str) -> CourtInformation | None:
        if not text:
            logging.warning("Could not extract court information from empty text")
            return None
        try:
            court_info: CourtInformation = self.court_extractor.invoke(self._get_prompt_court(text))
        except Exception as e:
            logging.warning(f"Could not extract court information from dispatch resolution: {e}")
            return None
        return court_info

    def extract_from_file_path(self, file_path: str) -> DispatchResolutionStructure | None:
        loader = PdfLoader(file_path)
        documents = loader.load()
        if len(documents) == 0:
            return None
        full_text = "\n\n".join([document.page_content for document in documents])
        return self.extract_from_text(full_text)

    def extract_from_text(self, text: str) -> DispatchResolutionStructure | None:
        if not text:
            logging.warning("Could not extract structure from empty dispatch resolution")
            return None
        try:
            structure: Structure = self.structure_extractor.invoke(self._get_prompt_structure(text))
        except Exception as e:
            logging.warning(f"Could not extract structure from dispatch resolution: {e}")
            return None
        return DispatchResolutionStructure(**structure.model_dump())
    
    def _get_prompt_court(self, content: str) -> str:
        prompt = f"""
        Consider the following content:
        <content>{content}</content>
        Extract relevant court information, as well as information about a legal case, if present.
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
