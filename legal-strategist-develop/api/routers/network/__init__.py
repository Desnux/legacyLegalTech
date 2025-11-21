from fastapi import APIRouter, Depends

from routers.base import get_api_key


router = APIRouter(prefix="/network", dependencies=[Depends(get_api_key)], tags=["Network"])


from . import (
    email,
)
