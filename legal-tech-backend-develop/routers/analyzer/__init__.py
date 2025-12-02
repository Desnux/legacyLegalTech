from fastapi import APIRouter

router = APIRouter(prefix="/analyze", tags=["Analyze"])


from . import (
    demand_text_analyzer,
)
