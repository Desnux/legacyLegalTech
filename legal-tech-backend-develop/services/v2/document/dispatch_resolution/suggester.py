from models.pydantic import RequestAnalysis
from services.v2.document.demand_text import DemandTextStructure
from services.v2.document.generic import GenericSuggester
from .models import DispatchResolutionInformation


class DispatchResolutionSuggester(GenericSuggester[DispatchResolutionInformation, DemandTextStructure]):
    """Dispatch resolution suggester."""

    def __init__(self) -> None:
        super().__init__()
    
    def _get_request_prompt(self, document: DispatchResolutionInformation) -> str:
        prompt = f"""
        Consider the following dispatch resolution sent by the court to the plaintiffs:
        <dispatch-resolution>{document.model_dump_json(include={"resolution_date", "resolution"})}</dispatch-resolution>
        Determine if it requires a formal response from the plaintiffs.
        """
        return prompt.strip()

    def _get_suggestion_prompt(
        self, 
        document: DispatchResolutionInformation, 
        demand_text: DemandTextStructure | None, 
        analysis: RequestAnalysis
    ) -> str:
        prompt = f"""
        Consider the following dispatch resolution sent by the court to the plaintiffs:
        <dispatch-resolution>{document.model_dump_json(include={"resolution_date", "resolution"})}</dispatch-resolution>

        In the context of a legal case, as an assistant that helps the plaintiffs:
        - Provide valid response suggestions in es_ES to the dispatch resolution.
        - Your suggestion will be considered and expanded upon by the user.
        - Include specific details, such as names, dates and amounts.
        """
        if analysis.requires_compromise:
            prompt += "- Include at least one suggestion that establishes a monetary compromise with the defendants, for example, reduced debt amount."
        elif analysis.requires_correction and demand_text:
            prompt += "- Include at least one suggestion that corrects errors or shortcomings in the demand text."
        if demand_text:
            prompt += f"""
            To generate the suggestions, consider the following segments of the demand text previously sent to the court, if relevant:
            <demand-text>{demand_text}</demand-text>
            """
        return prompt.strip()
