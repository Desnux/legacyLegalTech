import json
from pydantic import BaseModel, Field, model_validator, field_validator
from typing import TypeVar, Generic


class Metrics(BaseModel):
    """
    Performance metrics for document processing.
    
    Time breakdown:
    - time: Total time for the entire task (includes Textract, OpenAI, and processing overhead)
    - textract_time: Time spent specifically in AWS Textract processing (upload, job execution, result retrieval)
    - openai_times: Individual call times to OpenAI API (each element is one LLM invocation)
    - text_processing_time: Time spent processing text input (JSON parsing, validation)
    - merge_processing_time: Time spent merging information from multiple sources
    """
    label: str = Field(..., description="Task label")
    llm_invocations: int = Field(0, description="Times an external LLM was called")
    time: float = Field(0.0, description="Time spent during task, in seconds")
    submetrics: list["Metrics"] | None = Field(None, description="Subtasks metrics")
    text_processing_time: float = Field(0.0, description="Time spent processing text input")
    merge_processing_time: float = Field(0.0, description="Time spent merging information")
    textract_time: float = Field(0.0, description="Time spent in Textract processing (upload, job execution, result retrieval), in seconds")
    openai_times: list[float] = Field(default_factory=list, description="Individual OpenAI call times, in seconds")
    
    @field_validator('openai_times')
    @classmethod
    def validate_openai_times(cls, v: list[float]) -> list[float]:
        """Validate that all OpenAI times are non-negative."""
        for time_val in v:
            if time_val < 0:
                raise ValueError(f"OpenAI time must be non-negative, got {time_val}")
        return v
    
    @field_validator('textract_time')
    @classmethod
    def validate_textract_time(cls, v: float) -> float:
        """Validate that Textract time is non-negative."""
        if v < 0:
            raise ValueError(f"Textract time must be non-negative, got {v}")
        return v


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
