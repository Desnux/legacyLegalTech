from fastapi import APIRouter, Depends

from routers.base import get_api_key


router = APIRouter(prefix="/simulate", dependencies=[Depends(get_api_key)], tags=["Simulate"])


from . import (
    case_simulator,
)
