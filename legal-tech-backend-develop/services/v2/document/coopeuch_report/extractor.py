from langchain_core.documents import Document
from services.v2.document.generic import GenericExtractor
from .models import CoopeuchReportExtractorInput, CoopeuchReportExtractorOutput, CoopeuchReportInformation


class CoopeuchReportExtractor(GenericExtractor[CoopeuchReportExtractorInput, CoopeuchReportInformation, CoopeuchReportExtractorOutput]):
    """COOPEUCH report information extractor."""

    def __init__(self, input: CoopeuchReportExtractorInput) -> None:
        super().__init__(input, CoopeuchReportInformation, CoopeuchReportExtractorOutput, label="CoopeuchReport")

    def _create_prompt(self, source: str, partial_information: CoopeuchReportInformation | None) -> str:
        prompt = f"""
        Your task is to extract information from the pages of a coopeuch report about self fraud, in order to do this consider the following source:
        <source>{source}</source>
        """
        if partial_information:
            prompt += f"""
            There is information already extracted from previous pages: <information>{partial_information.model_dump_json()}</information>
            Update the information given the new pages in the source.
            """
        prompt += """
        When extracting amounts and currency types:
        - Dot is used for thousands separator, comma is used for decimals separator.
        - Unless USD or UF is specified, assume CLP currency type.
        When extracting the Article 5 presumptions, identify exactly which of the following hypotheses apply:
        - letter_b  (operación entre cuentas propias del usuario)
        - letter_c  (abonos transferidos 48h antes a cuentas del usuario)
        - letter_d  (usuario reconoció haber entregado claves)
        - letter_g  (usuario realizó la operación físicamente antes de solicitar)
        - letter_h  (operación con autenticación reforzada)
        """
        return prompt.strip()

    def _filter_documents(self, documents: list[Document]) -> list[Document]:
        CONCLUSION_KEYWORD = "Conclusión"
        APPENDIX_KEYWORD = "ANEXO"
        PAGE_THRESHOLD = 3
        
        found_conclusion = False
        filtered_docs = []
        
        for idx, doc in enumerate(documents):
            content = doc.page_content
            page_number = doc.metadata.get("page", idx)
            if CONCLUSION_KEYWORD in content:
                found_conclusion = True
            elif found_conclusion and (page_number > PAGE_THRESHOLD or APPENDIX_KEYWORD in content):
                break
            filtered_docs.append(doc)
        return filtered_docs
