from abc import ABC, abstractmethod
from langchain_core.runnables import Runnable
from models.pydantic import LegalSuggestion
from pydantic import BaseModel
from providers.openai import llm


class BaseSuggester(ABC):
    """Base class for all document suggesters."""

    def _create_structured_suggester(self, schema: dict | BaseModel) -> Runnable:
        return llm.with_structured_output(schema=schema, method="function_calling", strict=False)
