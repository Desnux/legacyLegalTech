from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from .tribunal import Tribunal


class Receptor(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    recepthor_external_id: UUID = Field(..., nullable=False, description="External receptor ID")
    name: str | None = Field(None, max_length=255, description="Receptor name")
    primary_email: str | None = Field(None, max_length=255, description="Primary email address")
    secondary_email: str | None = Field(None, max_length=255, description="Secondary email address")
    primary_phone: str | None = Field(None, max_length=50, description="Primary phone number")
    secondary_phone: str | None = Field(None, max_length=50, description="Secondary phone number")
    address: str | None = Field(None, max_length=255, description="Physical address")
    
    # Relationships
    details: list["ReceptorDetail"] = Relationship(back_populates="receptor")


class ReceptorDetail(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    receptor_id: UUID = Field(
        ...,
        foreign_key="receptor.id",
        nullable=False,
        description="Receptor ID"
    )
    tribunal_id: UUID | None = Field(
        None,
        foreign_key="tribunal.id",
        nullable=True,
        description="Tribunal ID"
    )
    
    # Relationships
    receptor: Receptor = Relationship(back_populates="details")
    tribunal: "Tribunal" = Relationship()