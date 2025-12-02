from fastapi import APIRouter

router = APIRouter(prefix="/law-firm", tags=["Law Firm"])

from . import (
    law_firm,
)
