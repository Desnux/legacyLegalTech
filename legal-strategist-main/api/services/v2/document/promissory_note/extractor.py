from services.v2.document.generic import GenericExtractor
from .models import PromissoryNoteExtractorInput, PromissoryNoteExtractorOutput, PromissoryNoteInformation


class PromissoryNoteExtractor(GenericExtractor[PromissoryNoteExtractorInput, PromissoryNoteInformation, PromissoryNoteExtractorOutput]):
    """Promissory note information extractor."""

    def __init__(self, input: PromissoryNoteExtractorInput) -> None:
        super().__init__(input, PromissoryNoteInformation, PromissoryNoteExtractorOutput, label="PromissoryNote")

    def _create_prompt(self, source: str, partial_information: PromissoryNoteInformation | None) -> str:
        prompt = f"""
        Your task is to extract information from the pages of a promissory note, in order to do this consider the following source:
        <source>{source}</source>
        """
        if partial_information:
            prompt += f"""
            There is information already extracted from previous pages: <information>{partial_information.model_dump_json()}</information>
            Update the information given the new pages in the source.
            """
        prompt += """
        When extracting promissory note identifier:
        - It may be a number like N° 12345 or N* 891, in this case output only the number.
        - It may be a generic document type name, such as Boleta garantía, in this case output in lowercase.
        - If you only find the N° beginning of an identifier, output an empty string.
        When extracting information about debtors and co-debtors:
        - Pay attention, they must be surrounded by either an identifier such as RUT or C.I.N, or labeled as a legal representative in the text.
        - Otherwise, ignore standalone names with noise in or around them, they are probably attached to signatures, in this case they are not relevant.
        """
        return prompt
