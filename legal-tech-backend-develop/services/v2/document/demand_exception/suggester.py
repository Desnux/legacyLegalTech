from models.pydantic import RequestAnalysis
from services.v2.document.demand_text import DemandTextStructure
from services.v2.document.generic import GenericSuggester
from .models import DemandExceptionInformation


class DemandExceptionSuggester(GenericSuggester[DemandExceptionInformation, DemandTextStructure]):
    """Demand exception suggester."""

    def __init__(self) -> None:
        super().__init__()
    
    def _get_request_prompt(self, document: DemandExceptionInformation) -> str:
        prompt = f"""
        Consider the following exceptions raised by the defendants:
        <exceptions>{[e.model_dump() for e in document.exceptions or []]}</exceptions>
        Determine if it requires a formal response from the plaintiffs.
        """
        return prompt.strip()

    def _get_suggestion_prompt(
        self, 
        document: DemandExceptionInformation, 
        demand_text: DemandTextStructure | None, 
        analysis: RequestAnalysis
    ) -> str:
        prompt = f"""
        Consider the following exceptions raised by the defendants:
        <exceptions>{ " ".join([e.model_dump_json() for e in document.exceptions or []]) }</exceptions>
        
        In the context of a legal case, as an assistant that helps the plaintiffs:
        - Provide valid response suggestions in es_ES.
        - Your suggestion will be considered and expanded upon by the user.
        - Include specific details, such as names, dates and amounts, if provided.
        - Include at least one RESPONSE or EXCEPTIONS_RESPONSE suggestion if there is an exception; if there are multiple exceptions, provide a suggestion that addresses them all.
        """
        if analysis.requires_compromise:
            prompt += " - Include at least one suggestion that establishes a monetary compromise with the defendants."
        if demand_text:
            prompt += f"""
            To generate the suggestions, consider the following segments of the demand text previously sent to the court:
            <demand-text>{demand_text.model_dump_json(include={"opening", "missing_payment_arguments", "main_request", "additional_requests"})}</demand-text>
            """
        return prompt.strip()
