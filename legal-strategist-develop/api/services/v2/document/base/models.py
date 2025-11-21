import json
from pydantic import BaseModel, Field, model_validator
from typing import TypeVar, Generic


class Metrics(BaseModel):
    """Performance metrics."""
    label: str = Field(..., description="Task label")
    llm_invocations: int = Field(0, description="Times an external LLM was called")
    time: float = Field(0.0, description="Time spent during task, in seconds")
    submetrics: list["Metrics"] | None = Field(None, description="Subtasks metrics")


class InformationBaseModel(BaseModel):
    """Information of a given document."""

    def normalize(self) -> None:
        """Normalizes all fields and subfields."""
        return


class InputBaseModel(BaseModel):
    """Base model for JSON serializable input."""
    
    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class ExtractorInputBaseModel(InputBaseModel):
    """Base model for JSON serializable extractor input."""
    content: str | None = Field(None, description="Content to extract from")
    file_path: str | None = Field(None, description="File path of PDF file to extract from")


InformationType = TypeVar("InformationType", bound=InformationBaseModel)


class OutputBaseModel(BaseModel, Generic[InformationType]):
    """Base model for JSON serializable output."""
    metrics: Metrics | None = Field(None, description="Output metrics")
    structured_output: InformationType | None = Field(None, description="Output information")

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class Response(BaseModel):
    output: str | None = Field(None, description="Output")


class ResponseList(BaseModel):
    output: list[str] | None = Field(None, description="Output")
