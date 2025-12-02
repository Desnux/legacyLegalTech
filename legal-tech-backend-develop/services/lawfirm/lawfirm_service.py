import logging
from sqlmodel import Session, select

from models.sql import LawFirm
from models.pydantic.law_firm import LawFirmCreate, LawFirmResponse


def create_law_firm(session: Session, law_firm_data: LawFirmCreate) -> LawFirmResponse:
    """
    Create a new law firm in the database.
    
    Args:
        session: Database session
        law_firm_data: Law firm data to create
        
    Returns:
        LawFirmResponse with the created law firm data
        
    Raises:
        Exception: If there's an error creating the law firm
    """
    try:
        # Create the law firm
        law_firm = LawFirm(
            rut=law_firm_data.rut,
            name=law_firm_data.name,
            description=law_firm_data.description
        )
        
        session.add(law_firm)
        session.commit()
        session.refresh(law_firm)
        
        # Convert to response model
        return LawFirmResponse(
            id=str(law_firm.id),
            rut=law_firm.rut,
            name=law_firm.name,
            description=law_firm.description
        )
        
    except Exception as e:
        session.rollback()
        logging.error(f"Error creating law firm: {e}")
        raise


def get_all_law_firms(session: Session, skip: int = 0, limit: int = 10) -> list[LawFirmResponse]:
    """
    Get all law firms with pagination.
    
    Args:
        session: Database session
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        
    Returns:
        List of LawFirmResponse
        
    Raises:
        Exception: If there's an error querying the database
    """
    try:
        # Query law firms with pagination
        statement = select(LawFirm).offset(skip).limit(limit)
        law_firms = session.exec(statement).all()
        
        # Convert to response models
        result = []
        for law_firm in law_firms:
            result.append(LawFirmResponse(
                id=str(law_firm.id),
                rut=law_firm.rut,
                name=law_firm.name,
                description=law_firm.description
            ))
        
        return result
        
    except Exception as e:
        logging.error(f"Error getting law firms: {e}")
        raise

