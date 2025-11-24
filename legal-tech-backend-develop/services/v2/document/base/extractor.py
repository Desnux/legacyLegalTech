from abc import ABC, abstractmethod
from langchain_core.runnables import Runnable
from pydantic import BaseModel
from providers.openai import llm

from .models import OutputBaseModel


class BaseExtractor(ABC):
    """Base class for all document extractors."""
    @abstractmethod
    def extract(self) -> OutputBaseModel:
        """Subclasses must implement this method to generate structured output given an input."""
        pass

    def _create_structured_extractor(self, schema: dict | BaseModel) -> Runnable:
        return llm.with_structured_output(schema=schema, method="function_calling", strict=False)
