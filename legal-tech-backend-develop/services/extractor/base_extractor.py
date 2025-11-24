from abc import ABC

from langchain_core.runnables import Runnable
from pydantic import BaseModel

from providers.openai import ChatOpenAI, llm


class BaseExtractor(ABC):
    def get_extractor_model(self) -> ChatOpenAI:
        return llm 
    
    def get_structured_extractor(self, schema: dict | BaseModel) -> Runnable:
        return llm.with_structured_output(schema=schema, method="function_calling", strict=False)
