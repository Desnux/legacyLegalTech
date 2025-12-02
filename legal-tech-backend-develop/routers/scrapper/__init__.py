from fastapi import APIRouter

router = APIRouter(prefix="/scrapper", tags=["Scrapper"])


from . import (
    digital_curators,
)
