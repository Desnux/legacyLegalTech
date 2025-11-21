import asyncio
import logging
from fastapi import APIRouter, Body, Depends, File, UploadFile
from fastapi.responses import JSONResponse

from models.api import DemandTextSendRequest, DemandTextSendResponse, ErrorResponse
from models.pydantic import AnnexFile
from services.pjud import PJUDController
from routers.base import get_api_key


MAX_RETRIES = 3


router = APIRouter()


async def simulate_pjud_scraping() -> None:
    await asyncio.sleep(10)
    return DemandTextSendResponse(message="Valid", status=200)


@router.post("/demand_text/", response_model=DemandTextSendResponse, dependencies=[Depends(get_api_key)])
async def demand_text(
    input: DemandTextSendRequest = Body(..., description="PJUD data"),
    demand_text: UploadFile = File(..., description="Demand text PDF file"),
    contract: UploadFile = File(..., description="Contract PDF file"),
    mandate: UploadFile = File(..., description="Lawyer mandate PDF file"),
    extra_files: list[UploadFile] = File([], description="Additional PDF files", max_length=20),
    extra_files_labels: list[str] = File([], description="Additional PDF files labels", max_length=20),
):
    if demand_text.content_type != "application/pdf":
        error_response = ErrorResponse(error="Invalid demand text file type", code=400)
        return JSONResponse(status_code=400, content=error_response.model_dump())
    
    if contract.content_type != "application/pdf":
        error_response = ErrorResponse(error="Invalid contract file type", code=400)
        return JSONResponse(status_code=400, content=error_response.model_dump())
    
    if mandate.content_type != "application/pdf":
        error_response = ErrorResponse(error="Invalid mandate file type", code=400)
        return JSONResponse(status_code=400, content=error_response.model_dump())
    
    annexes = [
        AnnexFile(label="Contrato", upload_file=contract),
        AnnexFile(label="Mandato", upload_file=mandate),
    ]

    for label, file in zip(extra_files_labels, extra_files):
        annexes.append(AnnexFile(label=label, upload_file=file))
    
    controller = PJUDController()
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            controller_response = await simulate_pjud_scraping() #await controller.send_demand_to_pjud(input, demand_text, annexes)
            if controller_response is not None:
                return controller_response
        except Exception as e:
            logging.warning(f"Attempt {attempt} to send demand text failed with error: {e}")
            if attempt == MAX_RETRIES:
                error_response = ErrorResponse(error=f"Internal error: {e}", code=500)
                return JSONResponse(status_code=500, content=error_response.model_dump())
    
    error_response = ErrorResponse(error=f"Could not send demand text after {MAX_RETRIES} retries", code=500)
    return JSONResponse(status_code=500, content=error_response.model_dump())
