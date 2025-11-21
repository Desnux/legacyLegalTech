import logging
from pydantic import BaseModel, Field
from typing import TypeVar, Generic

from models.pydantic import (
    LegalSuggestion,
    RequestAnalysis,
    SuggestionType,
)
from services.v2.document.base import BaseSuggester, InformationBaseModel


class Response(BaseModel):
    suggestions: list[LegalSuggestion] | None = Field(None, description="List of possible suggestions")


InformationType = TypeVar("InformationType", bound=InformationBaseModel)
StructureType = TypeVar("StructureType", bound=InformationBaseModel)


class GenericSuggester(BaseSuggester, Generic[InformationType, StructureType]):
    """Generic document extractor to handle different document types."""

    def __init__(self) -> None:
        super().__init__()
        self.request_analyzer = self._create_structured_suggester(RequestAnalysis)
        self.suggestion_generator = self._create_structured_suggester(Response)

    def _get_request_prompt(self, document: InformationType) -> str:
        """Method to be overridden by subclasses to customize request prompt."""
        raise NotImplementedError("Subclasses must implement _create_prompt")

    def _get_suggestion_prompt(
        self, 
        document: InformationType, 
        demand_text: StructureType | None, 
        analysis: RequestAnalysis
    ) -> str:
        """Method to be overridden by subclasses to customize suggestion prompt."""
        raise NotImplementedError("Subclasses must implement _create_prompt")

    def generate_suggestions_from_structure(
        self, 
        document: InformationType, 
        demand_text: StructureType | None = None
    ) -> list[LegalSuggestion] | None:
        prompt_req = self._get_request_prompt(document)
        analysis: RequestAnalysis = self.request_analyzer.invoke(prompt_req)
        if not analysis.requires_response:
            return []
        
        prompt_sugg = self._get_suggestion_prompt(document, demand_text, analysis)
        response: Response = self.suggestion_generator.invoke(prompt_sugg)
        if not response.suggestions:
            logging.warning("No suggestions were generated")
            return None

        valid_suggestions = list(filter(lambda x: min(1.0, x.score or 0.0) > 0.5, response.suggestions))[:3]
        if not valid_suggestions:
            logging.warning("All suggestions have a score smaller than 0.5")
            return None
        valid_suggestions.sort(key=lambda x: x.score, reverse=True)

        for suggestion in valid_suggestions:
            if suggestion.suggestion_type == SuggestionType.RESPONSE:
                suggestion.suggestion_type = SuggestionType.EXCEPTIONS_RESPONSE

        return [LegalSuggestion(**suggestion.model_dump()) for suggestion in valid_suggestions]
