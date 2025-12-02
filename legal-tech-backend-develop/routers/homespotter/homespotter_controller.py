import logging
from fastapi import Path, HTTPException
from pathlib import Path as FilePath
import json

from models.api import error_response
from models.pydantic import OwnedPropertyDetailed, OwnedSociety, ActiveVehicle
from services.homespotter.client import HomeSpotterService
from config import Config
from . import router

service = HomeSpotterService()  # shared instance relying on HOMESPOTTER_API_KEY env var

# Load mocks once
MOCKS: dict[str, list] = {}
if Config.HOMESPOTTER_USE_MOCKS:
    mocks_path = FilePath(__file__).with_name("mocks.json")
    with mocks_path.open() as f:
        MOCKS = json.load(f)


@router.get(
    "/properties/by-owner/{rut}",
    response_model=list[OwnedPropertyDetailed],
    summary="All properties owned by RUT (HomeSpotter)",
)
async def properties_by_owner(rut: str = Path(..., description="RUT with verification digit")):
    """Return detailed properties owned by *rut* using HomeSpotter data."""
    try:
        if Config.HOMESPOTTER_USE_MOCKS:
            props = MOCKS.get("properties", {}).get(rut, [])
            return [OwnedPropertyDetailed.model_validate(p) for p in props]
        return service.list_person_properties(rut)
    except Exception as e:
        logging.warning(f"HomeSpotter properties_by_owner failed: {e}")
        raise HTTPException(status_code=500, detail=f"Could not fetch properties: {e}")


@router.get(
    "/vehicles/by-owner/{rut}",
    response_model=list[ActiveVehicle],
    summary="All vehicles owned by RUT (HomeSpotter)",
)
async def vehicles_by_owner(rut: str = Path(..., description="RUT with verification digit")):
    """Return vehicles owned by *rut* using the tenant report."""
    try:
        if Config.HOMESPOTTER_USE_MOCKS:
            vehs = MOCKS.get("vehicles", {}).get(rut, [])
            return [ActiveVehicle.model_validate(v) for v in vehs]
        return service.list_person_vehicles(rut)
    except Exception as e:
        logging.warning(f"HomeSpotter vehicles_by_owner failed: {e}")
        raise HTTPException(status_code=500, detail=f"Could not fetch vehicles: {e}")


@router.get(
    "/societies/by-owner/{rut}",
    response_model=list[OwnedSociety],
    summary="All societies where RUT is owner/shareholder (HomeSpotter)",
)
async def societies_by_owner(rut: str = Path(..., description="RUT with verification digit")):
    """Return societies where *rut* is shareholder using HomeSpotter data."""
    try:
        if Config.HOMESPOTTER_USE_MOCKS:
            socs = MOCKS.get("societies", {}).get(rut, [])
            return [OwnedSociety.model_validate(s) for s in socs]
        return service.list_person_societies(rut)
    except Exception as e:
        logging.warning(f"HomeSpotter societies_by_owner failed: {e}")
        raise HTTPException(status_code=500, detail=f"Could not fetch societies: {e}")
