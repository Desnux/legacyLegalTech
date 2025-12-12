from fastapi import APIRouter

router = APIRouter(prefix="/generate", tags=["Generate"])


from . import (
    demand_exception_generator,
    demand_exception__response,
    demand_text_generator,
    dispatch_resolution_generator,
    missing_payment_argument_generator,
    preliminary_measure_generator,
    withdrawal_generator,
)
