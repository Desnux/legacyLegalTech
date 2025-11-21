from fastapi import APIRouter, Depends

from routers.base import get_api_key


router = APIRouter(prefix="/suggest", dependencies=[Depends(get_api_key)], tags=["Suggest"])


from . import (
    demand_exception_suggester,
    dispatch_resolution_suggester,
)
