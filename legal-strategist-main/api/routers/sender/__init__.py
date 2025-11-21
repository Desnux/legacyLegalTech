from fastapi import APIRouter, Depends

from routers.base import get_api_key


router = APIRouter(prefix="/send", dependencies=[Depends(get_api_key)], tags=["Send"])


from . import (
    demand_sender,
    demand_text_sender,
)
