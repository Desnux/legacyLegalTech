from abc import ABC, abstractmethod
from langchain_core.runnables import Runnable
from pydantic import BaseModel
from providers.openai import llm

from .models import OutputBaseModel


class BaseAnalyzer(ABC):
    """Base class for all document analyzers."""
    @abstractmethod
    def analyze(self) -> OutputBaseModel:
        """Subclasses must implement this method to return an structured analysis given an input."""
        pass

    def _create_structured_analyzer(self, schema: dict | BaseModel) -> Runnable:
        return llm.with_structured_output(schema=schema, method="function_calling", strict=False)
