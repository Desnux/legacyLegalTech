from fastapi import APIRouter, Body, Depends
from fastapi.responses import JSONResponse

from models.api import DemandTextGenerationResponse, ErrorResponse
from models.pydantic import DemandTextCorrectionForm, JudicialCollectionDemandTextStructure
from services.corrector import DemandTextCorrector
from routers.base import get_api_key


router = APIRouter()


@router.post("/demand_text_by_structured/", response_model=DemandTextGenerationResponse, dependencies=[Depends(get_api_key)])
async def demand_text_by_structured_corrector(
    structured_output: JudicialCollectionDemandTextStructure = Body(..., description="Structured demand text output"),
    correction_form: DemandTextCorrectionForm = Body(..., description="Corrected demand text information")
):
    try:
        corrector = DemandTextCorrector(correction_form)
        demand_text = corrector.generate_from_structured_output(structured_output)
    except Exception as e:
        error_response = ErrorResponse(error=f"Internal error (demand text correction): {e}", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    
    if demand_text is None:
        error_response = ErrorResponse(error="Could not correct demand text", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    correction_form.update()
    return DemandTextGenerationResponse(raw_text=None, structured_output=demand_text, correction_form=correction_form)
