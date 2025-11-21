from abc import ABC

from langchain_core.runnables import Runnable
from pydantic import BaseModel

from providers.openai import ChatOpenAI, llm


class BaseAnalyzer(ABC):
    def get_analyzer_model(self) -> ChatOpenAI:
        return llm 
    
    def get_structured_analyzer(self, schema: dict | BaseModel) -> Runnable:
        return llm.with_structured_output(schema=schema, method="function_calling", strict=False)