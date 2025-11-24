from fastapi import APIRouter

router = APIRouter(prefix="/receptor", tags=["Receptor"])


from . import (
    receptor,
)
