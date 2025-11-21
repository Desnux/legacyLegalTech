from models.pydantic import PromissoryNote
from services.extractor.base_extractor import BaseExtractor
from services.loader import PdfLoader


class PromissoryNoteExtractor(BaseExtractor):
    def __init__(self, context: str = "") -> None:
        self.context = context.strip()
        self.extractor_llm = self.get_structured_extractor(PromissoryNote)

    def extract_from_file_path(self, file_path: str) -> PromissoryNote | None:
        loader = PdfLoader(file_path)
        documents = loader.load()
        if len(documents) == 0:
            return None
        promissory_note: PromissoryNote | None = None
        for document in documents:
            if len(document.page_content) < 16:
                continue
            promissory_note = self.extractor_llm.invoke(self._get_prompt(document.page_content, promissory_note))
            promissory_note.normalize()
        return promissory_note
    
    def _get_prompt(self, source: str, partial: PromissoryNote | None = None) -> str:
        if partial is None:
            prompt = f"Extract promissory note attributes from the source: <source>{source}</source>"
        else:
            prompt = f"This are partial promissory note attributes: <attributes>{partial.model_dump_json()}</attributes>"
            prompt += f"\nUpdate them given a new segment of the original document: <source>{source}</source>"
        if len(self.context) > 0:
            prompt += f"\nConsider additional context to help you extract attributes: <context>{self.context}</context>"
        if partial:
            prompt += """
            When extracting debtors and co-debtors:
            - Pay attention, they must be surrounded by either an identifier such as RUT or C.I.N, or labeled as a legal representative in the text.
            - Otherwise, ignore standalone names with noise in or around them, they are probably attached to signatures, in this case they are not relevant for your result.
            """
        return prompt
