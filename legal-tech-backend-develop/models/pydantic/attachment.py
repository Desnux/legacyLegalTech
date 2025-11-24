from pydantic import BaseModel, Field

from .enum import DocumentType


class AttachmentInformation(BaseModel):
    name: str | None = Field(None, description="Document name or title")
    document_type: DocumentType | str | None = Field(None, description="Type of the document based on its content")
    summary: str | None = Field(None, description="Summary of the document content, it should mention the sender and expected receiver in the context of a legal case")
    

class AttachmentInformationExtended(AttachmentInformation):
    content: str | None = Field(None, description="Raw content")
    key: str | None = Field(None, description="Document storage key")
