import json
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from .attorney import Attorney
from .creditor import Creditor
from .debtor import Debtor
from .legal_representative import LegalRepresentative


class SimulationInput(BaseModel):
    court_city: Optional[str] = Field(..., description="City where the court is located")
    creditors: Optional[list[Creditor]] = Field(..., description="Creditors or emitters of the promissory note")
    debtors: Optional[list[Debtor]] = Field(..., description="Main debtors or suscribers of the promissory note")
    co_debtors: Optional[list[Debtor]] = Field(None, description="Guaranteers or joint co-debtors of the promissory note")

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class SimulationJudicialCollectionDemandTextInput(BaseModel):
    legal_representatives: Optional[list[LegalRepresentative]] = Field(..., description="Legal representatives of the plaintiffs")
    sponsoring_attorneys: Optional[list[Attorney]] = Field(..., description="Sponsoring attorneys for the plaintiffs")


class SimulationJudicialCollectionDemandExceptionInput(BaseModel):
    defendant_attorneys: Optional[list[Attorney]] = Field(..., description="Defendant attorneys for the defendants")
