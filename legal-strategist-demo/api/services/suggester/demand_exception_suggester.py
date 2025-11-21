import logging

from pydantic import BaseModel, Field

from models.pydantic import DemandExceptionStructure, JudicialCollectionDemandTextStructure, LegalSuggestion, SuggestionType
from providers.openai import get_structured_generator


class RequestAnalysis(BaseModel):
    requires_response: bool | None = Field(None, description="True if the content requires a response because there is a request or need to counter an exception, False if everything is in order and the user should simply wait")
    requires_compromise: bool | None = Field(None, description="True if the content heavily favors the defendants to the point the plaintiff should seek a compromise, False otherwise")


class Response(BaseModel):
    suggestions: list[LegalSuggestion] | None = Field(None, description="List of possible 'exceptions_response', or 'compromise' suggestions")


class DemandExceptionSuggester:
    def __init__(self) -> None:
        self.request_analyzer = get_structured_generator(RequestAnalysis)
        self.suggestion_generator = get_structured_generator(Response)

    def generate_suggestions_from_structure(
            self, 
            demand_exception: DemandExceptionStructure, 
            demand_text: JudicialCollectionDemandTextStructure | None = None
        ) -> list[LegalSuggestion] | None:
        prompt = f"""
        Consider the following exceptions raised by the defendants:
        <exceptions>{demand_exception.model_dump_json(exclude={"header"})}</exceptions>
        Determine if it requires a formal response from the plaintiffs.
        """
        analysis: RequestAnalysis = self.request_analyzer.invoke(prompt)
        if not analysis.requires_response:
            return []

        prompt = self._get_prompt_suggestion(
            bool(analysis.requires_compromise),
            demand_exception.to_raw_text(),
            demand_text.model_dump_json(include={"opening", "missing_payment_arguments", "main_request", "additional_requests"}) if demand_text else None,
        )
        response: Response = self.suggestion_generator.invoke(prompt)
        if not response.suggestions:
            logging.warning("No suggestions were generated")
            return None
        valid_suggestions = list(filter(lambda x: min(1.0, x.score or 0.0) > 0.5, response.suggestions or []))[:3]
        if len(valid_suggestions) == 0:
            logging.warning("All suggestions have a score smaller than 0.5")
            return None
        valid_suggestions.sort(key=lambda x: x.score, reverse=True)
        for suggestion in valid_suggestions:
            if suggestion.suggestion_type == SuggestionType.RESPONSE:
                suggestion.suggestion_type = SuggestionType.EXCEPTIONS_RESPONSE
        return [LegalSuggestion(**suggestion.model_dump()) for suggestion in valid_suggestions]

    def _get_prompt_suggestion(self, requires_compromise: bool, demand_exception: str, demand_text: str | None) -> str:
        prompt = f"""
        Consider the following exceptions raised by the defendants:
        <exceptions>{demand_exception}</exceptions>

        In the context of a legal case, as an assistant that helps the plaintiffs:
        - Provide valid response suggestions in es_ES to the dispatch resolution.
        - Your suggestion will be considered and expanded upon by the user.
        - Do not create a suggestion for each exception, handle all them inside a single suggestion, if logical.
        - Include specific details, such as names, dates and amounts.
        """
        if requires_compromise:
            prompt += "- Include at least one suggestion that establishes a monetary compromise with the defendants, for example, reduced debt amount."
        if demand_text:
            prompt += f"""
            To generate the suggestions, consider the following segments of the demand text previously sent to the court, if relevant:
            <demand-text>{demand_text}</demand-text>
            """
        return prompt
