from fastapi import APIRouter, Depends

from routers.base import get_api_key


router = APIRouter(prefix="/scrapper", dependencies=[Depends(get_api_key)], tags=["Scrapper"])


from . import (
    digital_curators,
)
