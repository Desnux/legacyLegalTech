from fastapi import APIRouter

router = APIRouter(prefix="/courts", tags=["Courts"])

from . import (
    court,
)
