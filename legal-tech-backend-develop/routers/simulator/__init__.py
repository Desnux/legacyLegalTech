from fastapi import APIRouter

router = APIRouter(prefix="/simulate", tags=["Simulate"])

from . import (
    case_simulator,
)
