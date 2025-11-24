from typing import Optional

from fastapi import UploadFile
from pydantic import BaseModel, Field

from models.pydantic import MissingPaymentDocumentType


class AnnexFile(BaseModel):
    label: str = Field(..., description="File label")
    upload_file: UploadFile = Field(..., description="Upload file")


class MissingPaymentFile(BaseModel):
    document_type: MissingPaymentDocumentType = Field(..., description="Document type")
    file_path: Optional[str] = Field(None, description="Document file path")
    upload_file: Optional[UploadFile] = Field(None, description="FastAPI upload file")
    
