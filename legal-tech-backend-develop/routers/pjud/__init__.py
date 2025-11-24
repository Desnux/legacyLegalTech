from fastapi import APIRouter

router = APIRouter(prefix="/pjud", tags=["PJUD"])

from . import case_scrapper
from . import folios
