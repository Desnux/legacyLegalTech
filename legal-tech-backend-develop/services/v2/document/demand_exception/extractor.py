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
        When extracting information about court details:
        - Extract court_city from the "Tribunal" field or court name (e.g., "Santiago" from "4º Juzgado Civil de Santiago")
        - Extract court_number from the "Tribunal" field or court name (e.g., "4" from "4º Juzgado Civil de Santiago")
        - Extract case_role from the "Rol" field (e.g., "C-2524-2022", "C-1234-2024")
        - Extract case_title from the "Carátula" field (e.g., "Santander Consumer Finnace Limitada/Biadayoli")
        - Look for these fields in the document header, usually formatted as "Tribunal:", "Carátula:", "Rol:", "Cuaderno:"
        When extracting information about attorneys:
        - Consider only defendant attorneys, usually found in header or opening statements.
        - Look for attorney information in the party identification section (e.g., "por la parte ejecutada")
        When extracting information about exceptions:
        - Fix potential OCR errors.
        - Look for "Opone excepciones" or similar phrases in the summary section.
        """
        return prompt
