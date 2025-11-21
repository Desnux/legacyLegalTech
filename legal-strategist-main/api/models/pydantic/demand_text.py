from typing import Optional

from pydantic import BaseModel, Field

from .attorney import Attorney
from .defendant import Defendant
from .metrics import MetricsExtractor
from .plaintiff import Plaintiff


class DemandText(BaseModel):
    defendants: Optional[list[Defendant]] = Field(None, description="Defendants or ejecutados the case is against, may be None if missing information")
    plaintiffs: Optional[list[Plaintiff]] = Field(None, description="Plaintiffs or ejecutantes that want to start the case, may be None if missing information")
    requests: Optional[list[str]] = Field(None, description="Otrosí or additionals present in the text, in asc order, summarized in less than 15 words each, may be None if missing information")
    sponsoring_attorneys: Optional[list[Attorney]] = Field(None, description="Sponsoring attorneys of the plaintiffs, may be None if missing information")
    metrics: Optional[MetricsExtractor] = Field(None, description="Metrics of the extracted document information")


class DemandTextContext(BaseModel):
    context: Optional[str] = Field(None, description="Relevant context that may help with the query in less than 50 words")


class DemandTextRequests(BaseModel):
    main_request: Optional[str] = Field(..., description="Main request of the text, summarized in less than 15 words")
    additional_requests: Optional[list[str]] = Field(..., description="Otrosí or additionals present in the text, in asc order, summarized in less than 15 words each")
