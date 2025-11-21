import json

from pydantic import BaseModel, Field, model_validator

from models.pydantic import (
    DemandTextCorrectionForm,
    LegalSubject,
    JudicialCollectionDemandTextStructure,
    PJUDABDTE,
    PJUDDDO,
    PJUDDTE,
)


class DemandTextGenerationResponse(BaseModel):
    raw_text: str | None = Field(..., description="Raw text of a demand text related to a judicial collection")
    structured_output: JudicialCollectionDemandTextStructure | None = Field(..., description="Structured output of a demand text related to a judicial collection")
    correction_form: DemandTextCorrectionForm | None = Field(..., description="Extracted information that may be corrected")


class DemandTextSendRequest(BaseModel):
    password: str = Field(..., description="PJUD Password")
    rut: str = Field(..., description="PJUD RUT")
    legal_subject: LegalSubject = Field(LegalSubject.GENERAL_COLLECTION, description="Legal subject of the demand text")
    sponsoring_attorneys: list[PJUDABDTE] = Field(..., description="Entities for AB.DTE. roles")
    plaintiffs: list[PJUDDTE] = Field(..., description="Entities for DTE. roles")
    defendants: list[PJUDDDO] = Field(..., description="Entities for DDO. roles")

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class DemandTextSendResponse(BaseModel):
    message: str = Field(..., description="PJUD Response")
    status: int = Field(..., description="HTTP status code")
