from pydantic import BaseModel, Field
from uuid import UUID

from .enum import StorageType


class UploadFile(BaseModel):
    key: UUID = Field(..., description="Unique identifier for the file")
    storage_type: StorageType = Field("local", description="Where the file is stored")