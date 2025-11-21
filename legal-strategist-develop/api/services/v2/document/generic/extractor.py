import time
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import Type, TypeVar, Generic

from services.loader import PdfLoader
from services.v2.document.base import BaseExtractor, ExtractorInputBaseModel, InformationBaseModel, Metrics, OutputBaseModel


MAX_SOURCE_CHARACTERS = 4096 * 4


InformationType = TypeVar("InformationType", bound=InformationBaseModel)
InputType = TypeVar("InputType", bound=ExtractorInputBaseModel)
OutputType = TypeVar("OutputType", bound=OutputBaseModel[InformationType])


class GenericExtractor(BaseExtractor, Generic[InputType, InformationType, OutputType]):
    """Generic document extractor to handle different document types."""

    def __init__(self, input: InputType, information_model: Type[InformationType], output_model: Type[OutputType], label: str) -> None:
        super().__init__()
        self.input = input
        self.output_model = output_model
        self.extractor = self._create_structured_extractor(information_model)
        self.label = label

    def extract(self) -> OutputType:
        """Extract structured information from input."""
        information: InformationType | None = None
        metrics = Metrics(label=f"{self.label}.extract")
        start_time = time.time()

        documents: list[Document] = []
        if file_path := self.input.file_path:
            loader = PdfLoader(file_path)
            documents = loader.load()
        if content := self.input.content:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=MAX_SOURCE_CHARACTERS,
                chunk_overlap=0,
                length_function=len,
                is_separator_regex=False,
            )
            documents = text_splitter.create_documents([content])
        
        documents = self._filter_documents(documents)
        if documents:
            batch = ""
            for doc in documents:
                page_text = doc.page_content.strip()
                if len(batch) + len(page_text) > MAX_SOURCE_CHARACTERS:
                    information = self._process_batch(batch, information, metrics)
                    batch = ""
                batch += page_text + "\n\n"
            if batch:
                information = self._process_batch(batch, information, metrics)
    
        metrics.time = round(time.time() - start_time, 4)
        return self.output_model(metrics=metrics, structured_output=information if information is not None else None)

    def _create_prompt(self, source: str, partial_information: InformationType | None) -> str:
        """Method to be overridden by subclasses to customize prompt."""
        raise NotImplementedError("Subclasses must implement _create_prompt")
    
    def _filter_documents(self, documents: list[Document]) -> list[Document]:
        """Override to filter pages extracted before sending to AI extractor."""
        return documents

    def _process_batch(self, batch: str, information: InformationType | None, metrics: Metrics) -> InformationType:
        """Helper method to process a batch and update extracted information."""
        extracted_info: InformationType = self.extractor.invoke(self._create_prompt(batch, information))
        if extracted_info:
            extracted_info.normalize()
            metrics.llm_invocations += 1
        return extracted_info
