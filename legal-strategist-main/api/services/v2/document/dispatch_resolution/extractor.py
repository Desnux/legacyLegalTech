from services.v2.document.generic import GenericExtractor
from .models import DispatchResolutionExtractorInput, DispatchResolutionExtractorOutput, DispatchResolutionInformation


class DispatchResolutionExtractor(GenericExtractor[DispatchResolutionExtractorInput, DispatchResolutionInformation, DispatchResolutionExtractorOutput]):
    """Dispatch resolution information extractor."""

    def __init__(self, input: DispatchResolutionExtractorInput) -> None:
        super().__init__(input, DispatchResolutionInformation, DispatchResolutionExtractorOutput, label="DispatchResolution")

    def _create_prompt(self, source: str, partial_information: DispatchResolutionInformation | None) -> str:
        prompt = f"""
        Your task is to extract information from the pages of a dispatch resolution, in order to do this consider the following source:
        <source>{source}</source>
        """
        if partial_information:
            prompt += f"""
            There is information already extracted from previous pages: <information>{partial_information.model_dump_json()}</information>
            Update the information given the new pages in the source.
            """
        prompt += """
        When extracting information about resolution date:
        - Transform human readable date in header to python date value.
        When extracting information about resolution:
        - Consider the content between footer and header and fix potential OCR errors.
        """
        return prompt
