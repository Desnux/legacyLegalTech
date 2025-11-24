from pydantic import BaseModel, Field


class DemandInformation(BaseModel):
    title: str = Field(..., description="Demand title")
    creation_date: str = Field(..., description="Demand creation date")
    court: str = Field(..., description="Court where the demand was submitted to")
    legal_subject: str = Field(..., description="Demand legal subject")
    author: str = Field(..., description="Demand author")
    index: int = Field(..., description="Demand index")
