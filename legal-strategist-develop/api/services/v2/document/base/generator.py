from abc import ABC, abstractmethod
from langchain_core.runnables import Runnable
from pydantic import BaseModel
from providers.openai import llm

from .models import OutputBaseModel


class BaseGenerator(ABC):
    """Base class for all document generators."""
    @abstractmethod
    def generate(self) -> OutputBaseModel:
        """Subclasses must implement this method to generate structured output given an input."""
        pass

    def _create_common_instructions(self) -> str:
        prompt = """
        When answering:
        - Generate your response in es_ES.
        - Consider that the information may match template placeholders values regardless of differences in plurality.
        - Adjust the inserted information and/or the text around it to ensure the result reads naturally, for example when dealing with plural or singular entities.
        - Use titlecase when filling up names and addresses, but do not change the casing of abbreviations, for example, SpA, S.A, L.M. must remain as is.
        - Do not use fake or example data to replace placeholders, use only real data provided inside the information tags.
        - If you are missing information to replace a placeholder, remove the placeholder from the filled template and adjust the text around it so it reads naturally, NEVER leave a placeholder in.
        - Add honorifics to names of people other than attorneys, such as don or doña, exclude them from names of groups, businesses or institutions.
        """
        return prompt

    def _create_structured_generator(self, schema: dict | BaseModel) -> Runnable:
        return llm.with_structured_output(schema=schema, method="function_calling", strict=False)
