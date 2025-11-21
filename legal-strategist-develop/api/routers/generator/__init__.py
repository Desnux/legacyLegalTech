from fastapi import APIRouter, Depends

from routers.base import get_api_key


router = APIRouter(prefix="/generate", dependencies=[Depends(get_api_key)], tags=["Generate"])


from . import (
    demand_exception_generator,
    demand_text_generator,
    dispatch_resolution_generator,
    missing_payment_argument_generator,
    preliminary_measure_generator,
    withdrawal_generator,
)
