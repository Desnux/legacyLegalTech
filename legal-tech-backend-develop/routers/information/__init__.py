from fastapi import APIRouter

router = APIRouter(prefix="/information", tags=["Information"])

from . import (
    statistics,
)
