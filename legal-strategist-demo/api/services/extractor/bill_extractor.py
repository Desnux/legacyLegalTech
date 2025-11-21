from models.pydantic import Bill
from services.extractor.base_extractor import BaseExtractor
from services.loader import PdfLoader


class BillExtractor(BaseExtractor):
    def __init__(self, context: str | None = None) -> None:
        self.context = context.strip() if context else ""
        self.extractor_llm = self.get_structured_extractor(Bill)

    def extract_from_file_path(self, file_path: str) -> Bill | None:
        loader = PdfLoader(file_path)
        documents = loader.load()
        if len(documents) == 0:
            return None
        bill: Bill | None = None
        for document in documents:
            if len(document.page_content) < 16:
                continue
            bill = self.extractor_llm.invoke(self._get_prompt(document.page_content, bill))
            bill.normalize()
        return bill
    
    def _get_prompt(self, source: str, partial: Bill | None = None) -> str:
        if partial is None:
            prompt = f"Extract bill attributes from the source: <source>{source}</source>"
        else:
            prompt = f"This are partial bill attributes: <attributes>{partial.model_dump_json()}</attributes>"
            prompt += f"\nUpdate them given a new segment of the original document: <source>{source}</source>"
        if len(self.context) > 0:
            prompt += f"\nConsider additional context to help you extract attributes: <context>{self.context}</context>"
        prompt += """
        When extracting bill identifier:
        - It usually follows a Nº character.
        When extracting debtors:
        - Pay attention, they must be surrounded by an identifier such as RUT or C.I.N. They are usually the first name mentioned after the identifier.
        """
        return prompt
