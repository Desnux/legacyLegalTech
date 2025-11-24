from fastapi import APIRouter

router = APIRouter(prefix="/tribunals", tags=["Tribunals"])

from . import (
    tribunal,
)
