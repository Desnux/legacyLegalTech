from fastapi import APIRouter, Depends

from routers.base import get_api_key


router = APIRouter(prefix="/analyze", dependencies=[Depends(get_api_key)], tags=["Analyze"])


from . import (
    demand_text_analyzer,
)
