import logging
from uuid import UUID
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from models.api import ReceptorResponse, ReceptorDetailResponse
from models.api.receptor import TribunalWithCourtInfo
from models.sql.receptor import Receptor, ReceptorDetail
from models.sql.tribunal import Tribunal


def _map_receptors_to_response(receptors: list[Receptor]) -> list[ReceptorResponse]:
    """
    Helper function to map Receptor SQL models to ReceptorResponse API models.
    
    Args:
        receptors: List of Receptor SQL models with preloaded relationships
        
    Returns:
        List of ReceptorResponse API models
    """
    response = []
    for receptor in receptors:
        details_response = []
        for detail in receptor.details:
            tribunal_info = None
            if detail.tribunal:
                tribunal_info = TribunalWithCourtInfo(
                    id=detail.tribunal.id,
                    recepthor_id=detail.tribunal.recepthor_id,
                    name=detail.tribunal.name,
                    code=detail.tribunal.code,
                    court_id=detail.tribunal.court_id,
                    court_name=detail.tribunal.court.name if detail.tribunal.court else None,
                    court_code=detail.tribunal.court.code if detail.tribunal.court else None
                )
            
            details_response.append(
                ReceptorDetailResponse(
                    id=detail.id,
                    tribunal=tribunal_info
                )
            )
        
        response.append(
            ReceptorResponse(
                id=receptor.id,
                recepthor_external_id=receptor.recepthor_external_id,
                name=receptor.name,
                primary_email=receptor.primary_email,
                secondary_email=receptor.secondary_email,
                primary_phone=receptor.primary_phone,
                secondary_phone=receptor.secondary_phone,
                address=receptor.address,
                details=details_response
            )
        )
    
    return response


def get_receptors(session: Session, skip: int = 0, limit: int = 10) -> list[ReceptorResponse]:
    """
    Get all receptors with pagination and their tribunal associations.
    
    Args:
        session: Database session
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        
    Returns:
        List of ReceptorResponse with tribunal details
        
    Raises:
        Exception: If there's an error querying the database
    """
    try:
        statement = (
            select(Receptor)
            .options(
                selectinload(Receptor.details)
                .selectinload(ReceptorDetail.tribunal)
                .selectinload(Tribunal.court)
            )
            .offset(skip)
            .limit(limit)
            .order_by(Receptor.name.asc())
        )
        
        receptors = session.exec(statement).unique().all()
        return _map_receptors_to_response(receptors)
        
    except Exception as e:
        logging.error(f"Error getting receptors: {e}")
        raise


def get_receptors_by_tribunal(session: Session, tribunal_id: UUID) -> list[ReceptorResponse]:
    """
    Get all receptors associated with a specific tribunal.
    
    Args:
        session: Database session
        tribunal_id: UUID of the tribunal to filter by
        
    Returns:
        List of ReceptorResponse associated with the tribunal
        
    Raises:
        Exception: If there's an error querying the database
    """
    try:
        receptor_details = session.exec(
            select(ReceptorDetail).where(ReceptorDetail.tribunal_id == tribunal_id)
        ).all()
        
        if not receptor_details:
            return []
        
        receptor_ids = list(set([detail.receptor_id for detail in receptor_details]))
        
        statement = (
            select(Receptor)
            .where(Receptor.id.in_(receptor_ids))
            .options(
                selectinload(Receptor.details)
                .selectinload(ReceptorDetail.tribunal)
                .selectinload(Tribunal.court)
            )
            .order_by(Receptor.name.asc())
        )
        
        receptors = session.exec(statement).unique().all()
        return _map_receptors_to_response(receptors)
        
    except Exception as e:
        logging.error(f"Error getting receptors by tribunal: {e}")
        raise

