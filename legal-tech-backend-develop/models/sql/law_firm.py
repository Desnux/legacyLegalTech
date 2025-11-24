from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID, uuid4


if TYPE_CHECKING:
    from .user import User


class LawFirm(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    rut: str = Field(..., description="RUT de la firma de abogados")
    name: str = Field(..., description="Nombre de la firma de abogados")
    description: str | None = Field(None, description="Descripción de la firma de abogados")
    
    # Relationships
    users: list["User"] = Relationship(back_populates="law_firm")
