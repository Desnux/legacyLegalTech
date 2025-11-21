from services.v2.document.generic import GenericExtractor
from .models import DemandExceptionExtractorInput, DemandExceptionExtractorOutput, DemandExceptionInformation


class DemandExceptionExtractor(GenericExtractor[DemandExceptionExtractorInput, DemandExceptionInformation, DemandExceptionExtractorOutput]):
    """Demand exception information extractor."""

    def __init__(self, input: DemandExceptionExtractorInput) -> None:
        super().__init__(input, DemandExceptionInformation, DemandExceptionExtractorOutput, label="DemandException")

    def _create_prompt(self, source: str, partial_information: DemandExceptionInformation | None) -> str:
        prompt = f"""
        Your task is to extract information from the pages of a document of exceptions to a demand, in order to do this consider the following source:
        <source>{source}</source>
        """
        if partial_information:
            prompt += f"""
            There is information already extracted from previous pages: <information>{partial_information.model_dump_json()}</information>
            Update the information given the new pages in the source.
            """
        prompt += """
        When extracting information about attorneys:
        - Consider only defendant attorneys, usually found in header or opening statements.
        When extracting information about exceptions:
        - Fix potential OCR errors.
        """
        return prompt
