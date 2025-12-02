from fastapi import APIRouter

router = APIRouter(prefix="/send", tags=["Send"])

from . import (
    demand_sender,
    demand_text_sender,
)
