from typing import Optional

from pydantic import BaseModel, Field


class MetricsExtractor(BaseModel):
    completeness: Optional[float] = Field(..., description="Value between 0.0 and 1.0 (inclusive), where 0.0 represents a document without the necessary information to start a case, and 1.0 represents a document with information about the plaintiffs, defendants, and what the demand is about")
    readability: Optional[float] = Field(..., description="Value between 0.0 and 1.0 (inclusive), where 0.0 represents an unreadable document full of noise, and 1.0 represents completely understandable document, without spelling mistakes")
    formality: Optional[float] = Field(..., description="Value between 0.0 and 1.0 (inclusive), where 0.0 represents an unserious and disrespectful document that contains vulgarities, and 1.0 represents a serious document written in impersonal tone, using legal vocabulary")