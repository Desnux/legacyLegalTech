from services.v2.document.generic import GenericExtractor
from .models import BillExtractorInput, BillExtractorOutput, BillInformation


class BillExtractor(GenericExtractor[BillExtractorInput, BillInformation, BillExtractorOutput]):
    """Bill information extractor."""

    def __init__(self, input: BillExtractorInput) -> None:
        super().__init__(input, BillInformation, BillExtractorOutput, label="BillExtractor")

    def _create_prompt(self, source: str, partial_information: BillInformation | None) -> str:
        prompt = f"""
        Your task is to extract information from the pages of a bill, in order to do this consider the following source:
        <source>{source}</source>
        """
        if partial_information:
            prompt += f"""
            There is information already extracted from previous pages: <information>{partial_information.model_dump_json()}</information>
            Update the information given the new pages in the source.
            """
        prompt += """
        When extracting information about the identifier:
        - It usually follows a Nº character.
        When extracting information about debtors:
        - Pay attention, they must be surrounded by an identifier such as RUT or C.I.N. They are usually the first name mentioned after the identifier.
        """
        return prompt
