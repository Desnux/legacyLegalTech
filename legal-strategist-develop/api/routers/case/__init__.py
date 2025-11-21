from fastapi import APIRouter, Depends

from routers.base import get_api_key


router = APIRouter(prefix="/case", dependencies=[Depends(get_api_key)], tags=["Case"])


from . import (
    case,
)
