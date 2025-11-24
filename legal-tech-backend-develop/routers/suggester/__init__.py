from fastapi import APIRouter

router = APIRouter(prefix="/suggest", tags=["Suggest"])


from . import (
    demand_exception_suggester,
    dispatch_resolution_suggester,
)
