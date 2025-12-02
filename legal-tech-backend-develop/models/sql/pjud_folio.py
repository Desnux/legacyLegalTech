from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, UniqueConstraint, Date
from sqlmodel import Field, SQLModel


class PJUDFolio(SQLModel, table=True):
    """Model for storing PJUD case notebook folios"""
    __tablename__ = "pjud_folios"

    id: int = Field(primary_key=True, index=True)
    folio_number: int = Field(..., index=True, description="Folio number")
    case_number: str = Field(..., max_length=20, index=True, description="Case number")
    year: int = Field(..., index=True, description="Case year")
    document: str | None = Field(None, max_length=50, description="Document name")
    stage: str | None = Field(None, max_length=100, description="Case stage")
    procedure: str | None = Field(None, max_length=100, description="Procedure type")
    procedure_description: str | None = Field(None, sa_column=Column(Text), description="Procedure description")
    procedure_date: date | None = Field(None, description="Procedure date")
    page: int | None = Field(None, description="Page number")
    milestone: str | None = Field(None, max_length=50, description="Case milestone")
    
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, 
        sa_column=Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
        description="Last update timestamp"
    )
    is_active: bool = Field(True, description="Whether the folio is active")
    
    scraping_session_id: str = Field(..., max_length=100, index=True, description="Scraping session ID (Format: YYYY-MM-DD-HH)")
    scraping_type: str = Field(..., max_length=20, description="Scraping type: full or incremental")
    
    __table_args__ = (
        UniqueConstraint('folio_number', 'case_number', 'year', 'procedure_description', name='uq_folio_case_year_description'),
    )

    def __repr__(self) -> str:
        return f"<PJUDFolio(id={self.id}, folio_number={self.folio_number}, case_number={self.case_number}, year={self.year}, milestone={self.milestone})>"
