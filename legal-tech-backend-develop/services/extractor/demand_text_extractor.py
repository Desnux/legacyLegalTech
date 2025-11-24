import logging

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field

from models.pydantic import (
    Attorney,
    DemandText,
    DemandTextContext,
    DemandTextRequests,
    JudicialCollectionDemandTextInput,
    JudicialCollectionLegalRequest,
    JudicialCollectionSecondaryRequest,
    LegalException,
    LegalSubject,
    Plaintiff,
)
from services.extractor.base_extractor import BaseExtractor
from services.loader import PdfLoader


class DemandTextRequestContext(BaseModel):
    context: str | None = Field(None, description="Additional context of the legal request")


class DemandTextRequestInformation(BaseModel):
    nature: JudicialCollectionLegalRequest = Field(..., description="Nature of the legal request")
    name: str | None = Field(None, description="Legal request summarized name")
    content: str | None = Field(None, description="Content of the legal request")


class DemandTextInformation(BaseModel):
    legal_subject: LegalSubject | None = Field(None, description="Legal subject of the case behind the demand text")
    plaintiffs: list[Plaintiff] | None = Field(None, description="Plaintiffs or claimants behind the demand text")
    sponsoring_attorneys: list[Attorney] | None = Field(None, description="Sponsoring attorneys for the plaintiffs")
    secondary_requests: list[DemandTextRequestInformation] | None = Field(None, description="Secondary requests that apply to the demand text")
    main_request: str | None = Field(None, description="Main request behind filing the demand text, usually in the first paragraph after naming the court, before listing")
    reasons_per_document: list[str] | None = Field(None, description="List of reasons to argue about missing payments, zipped to a list of documents, each one only indicates what the debtor did not do, for example 'No dio pago de ...', and includes breakdown of capital, interest, and debt amounts, if available")


class DemandTextExtractor(BaseExtractor):
    def __init__(self, context: str = "") -> None:
        self.context = context.strip()
        self.extractor_llm = self.get_structured_extractor(DemandText)
        self.extractor_context_llm = self.get_structured_extractor(DemandTextContext)
        self.extractor_information_llm = self.get_structured_extractor(DemandTextInformation)
        self.extractor_request_context_llm = self.get_structured_extractor(DemandTextRequestContext)
        self.extractor_requests_llm = self.get_structured_extractor(DemandTextRequests)
    
    def extract_from_file_path(self, file_path: str) -> JudicialCollectionDemandTextInput | None:
        loader = PdfLoader(file_path)
        documents = loader.load()
        if len(documents) == 0:
            return None
        full_text = "\n\n".join([document.page_content for document in documents])
        information: DemandTextInformation = self.extractor_information_llm.invoke(self._get_prompt_raw(full_text, None))
        secondary_requests = [JudicialCollectionSecondaryRequest(nature=request.nature, context=request.content) for request in information.secondary_requests or []]
        for request in secondary_requests:
            template = request.nature.get_template()
            new_context: DemandTextRequestContext = self.extractor_request_context_llm.invoke(self._get_prompt_request_context(request.context, template))
            request.context = new_context.context
        result = JudicialCollectionDemandTextInput(**information.model_dump(exclude={"secondary_requests"}), secondary_requests=secondary_requests)
        result.normalize()
        return result

    def extract_from_text(self, text: str) -> DemandText | None:
        documents = self._get_documents(text)
        if len(documents) == 0:
            return None
        demand_text: DemandText | None = None
        for document in documents:
            demand_text = self.extractor_llm.invoke(self._get_prompt(document.page_content, demand_text))
        try:
            requests = self._extract_requests(text[100:1500])
        except Exception as e:
            logging.warning(f"Could not pinpoint requests: {e}")
            requests = []
        if len(requests) > 0:
            demand_text.requests = requests
        return demand_text
    
    def extract_for_exceptions_from_text(self, text: str, exceptions: list[LegalException]) -> dict[LegalException, str] | None:
        documents = self._get_documents(text)
        if len(documents) == 0:
            return None
        exceptions_context: dict[LegalException, str] = {}
        for exception_nature in exceptions:
            context: DemandTextContext | None = None
            for document in documents[1:]:
                try:
                    context = self.extractor_context_llm.invoke(self._get_prompt_for_exception(document.page_content, exception_nature, context))
                except Exception as e:
                    logging.warning(f"Could not extract context for exception {exception_nature.value}: {e}")
                    continue
            exceptions_context[exception_nature] = context.context
        if len(exceptions_context.keys()) == 0:
            return None
        return exceptions_context

    def _extract_requests(self, source: str) -> list[str]:
        requests: list[str] = []
        demand_text_requests: DemandTextRequests = self.extractor_requests_llm.invoke(self._get_prompt_requests(source))
        if demand_text_requests.main_request:
            requests.append(f"(MAIN) {demand_text_requests.main_request}")
        for i, additional_request in enumerate(demand_text_requests.additional_requests or []):
            requests.append(f"({i + 1}) {additional_request}")
        return requests

    def _get_documents(self, text: str) -> list[Document]:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=0,
            length_function=len,
            is_separator_regex=False,
        )
        return text_splitter.create_documents([text])

    def _get_prompt(self, source: str, partial: DemandText | None = None) -> str:
        if partial is None:
            prompt = f"Extract demand text attributes from the source: <source>{source}</source>"
            prompt += f"\nAlso assign metrics between 0.0 and 1.0 (inclusive) according to the quality of the source."
        else:
            prompt = f"This are partial demand text attributes: <attributes>{partial.model_dump_json()}</attributes>"
            prompt += f"\nUpdate them given a new segment of the original document: <source>{source}</source>"
        if len(self.context) > 0:
            prompt += f"\nConsider additional context to help you extract attributes: <context>{self.context}</context>"
        prompt += f"\nDO NOT create information from nothing, if an attribute is missing, you may use None or an equivalent value, and penalize the completeness score."
        return prompt
    
    def _get_prompt_for_exception(self, source: str, exception_nature: LegalException, partial: DemandTextContext | None = None) -> str:
        if partial is None:
            prompt = f"Extract context that may be relevant to raise a legal exception related to the following article: <article>{exception_nature.to_localized_string()}</article>, from the source: <source>{source}</source>"
        else:
            prompt = f"This is partial context that may be relevant to raise an exception related to the following article: <article>{exception_nature.to_localized_string()}</article>, <context>{partial.model_dump_json()}<context>"
            prompt += f"\nUpdate it or replace it given a new segment of the original document: <source>{source}</source>"
        prompt += f"\nIf the source has nothing relevant to the article, DO NOT INCLUDE IT.\nBe concise and only keep important information, your context should not exceed 50 words."
        return prompt
    
    def _get_prompt_raw(self, source: str, partial: str | None = None) -> str:
        if partial is None:
            prompt = f"Extract demand text attributes in es_ES from the source: <source>{source}</source>"
        else:
            prompt = f"This are partial demand text attributes: <attributes>{partial}</attributes>"
            prompt += f"\nUpdate them in es_ES given a new segment of the original document: <source>{source}</source>"
        if len(self.context) > 0:
            prompt += f"\nConsider additional context to help you extract attributes: <context>{self.context}</context>"
        prompt += f"\nDO NOT use examples or create information, if an attribute is missing, you may assign None or an equivalent value"
        return prompt
    
    def _get_prompt_request_context(self, context: str, template: str) -> str:
        prompt = f"""
        Consider this template: <template>{template}</template>
        Now consider this filled and extended template: <filled-template>{context}</filled-template>
        Work backwards to extract the context in es_ES that was used to generate the filled-template from the original template, as a human written string.
        Return only the context, without additional insight, and without any text that was present in the original template, for example:
            <template>Se solicitan todos los bienes disponibles a embargar.</template>
            <filled-template>Solo se solicitan los siguientes bienes:\n- Auto\n- Casa</filled-template>
        In this example, the context that dictates the difference, and should be your output, is "- Auto\n- Casa".
        If there isn't meaningful context that transformed template into filled-template, return empty string.
        """
        return prompt

    def _get_prompt_requests(self, source: str) -> str:
        prompt = f"Extract the main request and additional requests from the source: <source>{source}</source>"
        prompt += f"\nEvery additional request is enumerated, do not add, merge, or remove additional requests."
        return prompt
