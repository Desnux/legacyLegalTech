import re
from abc import ABC

from langchain_core.runnables import Runnable
from pydantic import BaseModel

from providers.openai import ChatOpenAI, llm, llm_template_filler


class BaseGenerator(ABC):
    def get_generator_model(self) -> ChatOpenAI:
        return llm
    
    def get_structured_generator(self, schema: dict | BaseModel) -> Runnable:
        return llm.with_structured_output(schema=schema, method="function_calling", strict=False)
    
    def get_structured_template_filler(self, schema: dict | BaseModel) -> Runnable:
        return llm_template_filler.with_structured_output(schema=schema, method="function_calling", strict=False)
    
    def get_last_partial_length(self) -> int:
        return 100

    def has_placeholder(self, s: str) -> bool:
        placeholder_pattern = r"\{[a-zA-Z0-9_\.]+\}"
        return bool(re.search(placeholder_pattern, s))
