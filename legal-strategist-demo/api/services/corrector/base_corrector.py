from abc import ABC

from langchain_core.runnables import Runnable
from pydantic import BaseModel

from providers.openai import llm


class BaseCorrector(ABC):
    def get_structured_corrector(self, schema: dict | BaseModel) -> Runnable:
        return llm.with_structured_output(schema=schema, method="function_calling", strict=False)
