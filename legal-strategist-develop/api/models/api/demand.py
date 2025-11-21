import json

from pydantic import BaseModel, Field, model_validator

from models.pydantic import DemandInformation


class DemandBaseRequest(BaseModel):
    password: str = Field(..., description="PJUD Password")
    rut: str = Field(..., description="PJUD RUT")

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class DemandBaseResponse(BaseModel):
    message: str = Field(..., description="PJUD Response")
    status: int = Field(..., description="HTTP status code")


class DemandDeleteRequest(DemandBaseRequest):
    index: int = Field(..., description="Demand index")


class DemandDeleteResponse(DemandBaseResponse):
    pass


class DemandListGetRequest(DemandBaseRequest):
    pass


class DemandListGetResponse(DemandBaseResponse):
    data: list[DemandInformation] = Field([], description="Demand list")


class DemandSendRequest(DemandBaseRequest):
    index: int = Field(..., description="Demand index")


class DemandSendResponse(DemandBaseResponse):
    pass
