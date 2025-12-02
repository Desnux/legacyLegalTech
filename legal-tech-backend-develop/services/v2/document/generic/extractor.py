import logging
import os
import time
import traceback
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
            # Load documents and capture Textract time
            loader = PdfLoader(file_path)
            documents = loader.load()
            # Get Textract time from loader (captured during parse())
            metrics.textract_time = round(loader.textract_time, 4)
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
            batch_count = 0
            try:
                for doc in documents:
                    page_text = doc.page_content.strip()
                    if len(batch) + len(page_text) > MAX_SOURCE_CHARACTERS:
                        batch_count += 1
                        information = self._process_batch(batch, information, metrics)
                        batch = ""
                    batch += page_text + "\n\n"
                if batch:
                    batch_count += 1
                    information = self._process_batch(batch, information, metrics)
            except Exception as batch_processing_error:
                logging.error(f"  ❌ [GenericExtractor] Error en procesamiento de batches: {type(batch_processing_error).__name__}: {batch_processing_error}")
                logging.error(f"  📋 [GenericExtractor] Stack trace: {traceback.format_exc()}")
                raise
    
        metrics.time = round(time.time() - start_time, 4)
        
        try:
            output = self.output_model(metrics=metrics, structured_output=information if information is not None else None)
            return output
        except Exception as output_error:
            logging.error(f"  ❌ [GenericExtractor] Error creando output_model: {type(output_error).__name__}: {output_error}")
            logging.error(f"  📋 [GenericExtractor] Stack trace: {traceback.format_exc()}")
            raise

    def _create_prompt(self, source: str, partial_information: InformationType | None) -> str:
        """Method to be overridden by subclasses to customize prompt."""
        raise NotImplementedError("Subclasses must implement _create_prompt")
    
    def _filter_documents(self, documents: list[Document]) -> list[Document]:
        """Override to filter pages extracted before sending to AI extractor."""
        return documents

    def _process_batch(self, batch: str, information: InformationType | None, metrics: Metrics) -> InformationType:
        """Helper method to process a batch and update extracted information."""
        try:
            prompt = self._create_prompt(batch, information)
            
            # Log OpenAI call timing
            openai_start = time.time()
            extracted_info: InformationType = self.extractor.invoke(prompt)
            openai_time = round(time.time() - openai_start, 4)
            
            # Always capture OpenAI time, even if extraction fails
            metrics.llm_invocations += 1
            metrics.openai_times.append(openai_time)
            logging.info(f"  🤖 [OpenAI] Llamada #{metrics.llm_invocations} completada en {openai_time:.4f}s")
            
            if extracted_info:
                try:
                    extracted_info.normalize()
                except Exception as normalize_error:
                    logging.error(f"  ❌ [GenericExtractor] Error en normalize(): {type(normalize_error).__name__}: {normalize_error}")
                    logging.error(f"  📋 [GenericExtractor] Stack trace: {traceback.format_exc()}")
                    raise
            return extracted_info
        except Exception as batch_error:
            logging.error(f"  ❌ [GenericExtractor] Error procesando batch: {type(batch_error).__name__}: {batch_error}")
            logging.error(f"  📋 [GenericExtractor] Stack trace: {traceback.format_exc()}")
            raise
