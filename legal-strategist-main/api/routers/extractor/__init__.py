from fastapi import APIRouter, Depends

from routers.base import get_api_key


router = APIRouter(prefix="/extract", dependencies=[Depends(get_api_key)], tags=["Extract"])


from . import (
    address_extractor,
    bill_extractor,
    coopeuch_report_extractor,
    demand_exception_extractor,
    demand_list_extractor,
    demand_text_extractor,
    demand_text_input_extractor,
    dispatch_resolution_extractor,
    preliminary_measure_input_extractor,
    promissory_note_extractor,
)
