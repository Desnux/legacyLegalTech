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
        When extracting amounts:
        - Pay special attention to whether the amount appears to be handwritten or printed
        - Look for visual indicators: softer colors, less defined edges, more rounded letter shapes
        - Consider if the amount appears with different visual quality (less sharp, more organic shapes)
        - Handwritten text typically has: rounded letters, softer ink color, less precise edges, more natural curves
        - Machine-printed text typically has: sharp edges, consistent color, precise geometric shapes, uniform spacing
        - IMPORTANT: Handwritten amounts often appear next to words like "suma", "valor", "importe", "total", "monto", or similar terms
        - Look for amounts that are written in the blank space next to printed labels like "Por la suma de:", "Valor:", "Importe:", etc.
        - Set handwritten_amount to true if the amount clearly appears handwritten, false if printed/typed, or null if uncertain
        """
        return prompt
