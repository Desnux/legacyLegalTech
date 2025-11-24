from enum import Enum
from pydantic import BaseModel, Field


class AnalysisStatus(str, Enum):
    GOOD = "good"
    WARNING = "warning"
    ERROR = "error"


class AnalysisTag(str, Enum):
    CONTRADICTION = "contradiction"
    BAD_SPELLING = "bad_spelling"
    BAD_MATH = "bad_math"
    MISSING_INFO = "missing_info"
    TOO_REPETITIVE = "too_repetitive"
    INFORMAL_LANGUAGE = "informal_language"
    FALSE_INFORMATION = "false_information"
    POSSIBLE_OCR_ERROR = "possible_ocr_error"


class Analysis(BaseModel):
    feedback: str | None = Field(None, description="Feedback about the content, either positive or negative, if positive just declare that the content meets all requirementes, do not explain further")
    improvement_suggestions: str | None = Field(None, description="Suggestions to improve the content, if any")
    tags: list[AnalysisTag | str] | None = Field(None, description="Tags that describe the type of issues or strengths found in the analysis")
    status: AnalysisStatus | None = Field(None, description="Overall status of the content, 'good' if everything is in order, 'warning' if there are things to improve, 'error' if there are many critical issues")
    score: float | None = Field(None, description="Overall score of the content, from 0.0 to 1.0, where 0.0 indicates that there are many critical issues, and 1.0 indicates that everything is in order")


class ProbableCaseStats(BaseModel):
    compromise_amount_percentage: float | None = Field(None, description="Percentage amount to compromise for")
    compromise_chance: float | None = Field(None, description="Probable chance to reach a compromise")
    days_to_resolve: int | None = Field(None, description="Probable days to resolve to judicial means")
    withdrawal_chance: float | None = Field(None, description="Probable chance for a tactical withdrawal")


class RequestAnalysis(BaseModel):
    requires_response: bool | None = Field(None, description="True if the content requires a response because there is a request or need to counter an exception, False if everything is in order and the user should simply wait")
    requires_compromise: bool | None = Field(None, description="True if the content heavily favors the defendants to the point the plaintiff should seek a compromise, False otherwise")
    requires_correction: bool | None = Field(None, description="True if the content requires a response because there is a need of correction, False otherwise")
