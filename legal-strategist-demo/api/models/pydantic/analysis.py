from enum import Enum
from typing import Optional

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
    feedback: Optional[str] = Field(None, description="Feedback about the content, either positive or negative, if positive just declare that the content meets all requirementes, do not explain further")
    improvement_suggestions: Optional[str] = Field(None, description="Suggestions to improve the content, if any")
    tags: Optional[list[AnalysisTag | str]] = Field(None, description="Tags that describe the type of issues or strengths found in the analysis")
    status: Optional[AnalysisStatus] = Field(None, description="Overall status of the content, 'good' if everything is in order, 'warning' if there are things to improve, 'error' if there are many critical issues")
    score: Optional[float] = Field(None, description="Overall score of the content, from 0.0 to 1.0, where 0.0 indicates that there are many critical issues, and 1.0 indicates that everything is in order")
