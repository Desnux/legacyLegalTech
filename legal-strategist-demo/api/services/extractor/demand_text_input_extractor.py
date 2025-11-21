from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from models.pydantic import JudicialCollectionDemandTextInput, LegalSubject
from services.extractor.base_extractor import BaseExtractor


class DemandTextInputExtractor(BaseExtractor):
    def __init__(self) -> None:
        self.extractor_llm = self.get_structured_extractor(JudicialCollectionDemandTextInput)

    def extract_from_text(self, text: str) -> JudicialCollectionDemandTextInput | None:
        documents = self._get_documents(text)
        if len(documents) == 0:
            return None
        demand_text_input: JudicialCollectionDemandTextInput | None = None
        for document in documents:
            demand_text_input = self.extractor_llm.invoke(self._get_prompt(document.page_content, demand_text_input))
        if demand_text_input:
            demand_text_input.legal_subject = LegalSubject.PROMISSORY_NOTE_COLLECTION
        return demand_text_input
    
    def _get_documents(self, text: str) -> list[Document]:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=0,
            length_function=len,
            is_separator_regex=False,
        )
        return text_splitter.create_documents([text])

    def _get_prompt(self, source: str, partial: JudicialCollectionDemandTextInput | None = None) -> str:
        if partial is None:
            prompt = f"Extract attributes necessary to create a demand text from the source: <source>{source}</source>"
        else:
            prompt = f"This are attributes necessary to create a demand text: <attributes>{partial.model_dump_json()}</attributes>"
            prompt += f"\nUpdate them given a new segment of the original source: <source>{source}</source>"
        prompt += f"\nDO NOT create information from nothing, if an attribute is missing, you may use None or an equivalent value."
        return prompt
