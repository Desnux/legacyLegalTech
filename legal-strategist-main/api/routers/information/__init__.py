from fastapi import APIRouter, Depends

from routers.base import get_api_key


router = APIRouter(prefix="/information", dependencies=[Depends(get_api_key)], tags=["Information"])


from . import (
    statistics,
)
