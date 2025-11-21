from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import JSONResponse

from models.pydantic import ErrorResponse, JudicialCollectionDemandTextAnalysis, JudicialCollectionDemandTextStructure
from services.analyzer import DemandTextAnalyzer
from routers.base import get_api_key


router = APIRouter()


@router.post("/judicial_collection_demand_text_by_file/", response_model=JudicialCollectionDemandTextAnalysis, dependencies=[Depends(get_api_key)])
async def judicial_collection_demand_text_by_file_analyzer(
    input: UploadFile = File(..., description="PDF demand text file to analyze"),
    control: UploadFile = File(..., description="PDF demand text file to compare to"),
):
    if input.content_type != "application/pdf":
        error_response = ErrorResponse(error="Invalid input file type", code=400)
        return JSONResponse(status_code=400, content=error_response.model_dump())
    if control.content_type != "application/pdf":
        error_response = ErrorResponse(error="Invalid control file type", code=400)
        return JSONResponse(status_code=400, content=error_response.model_dump())
    try:
        analyzer = DemandTextAnalyzer()
        demand_text_analysis = analyzer.analyze_from_files(input, control)
    except Exception as e:
        error_response = ErrorResponse(error=f"Internal error: {e}", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    
    if demand_text_analysis is None:
        error_response = ErrorResponse(error="Could not analyze demand text", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    return demand_text_analysis


@router.post("/judicial_collection_demand_text_by_mixed/", response_model=JudicialCollectionDemandTextAnalysis, dependencies=[Depends(get_api_key)])
async def judicial_collection_demand_text_by_mixed_analyzer(
    input: JudicialCollectionDemandTextStructure = Form(..., description="Structured demand text to analyze"),
    control: UploadFile = File(..., description="PDF demand text file to compare to"),
):
    if control.content_type != "application/pdf":
        error_response = ErrorResponse(error="Invalid control file type", code=400)
        return JSONResponse(status_code=400, content=error_response.model_dump())
    try:
        analyzer = DemandTextAnalyzer()
        demand_text_analysis = analyzer.analyze_from_mixed(input, control)
    except Exception as e:
        error_response = ErrorResponse(error=f"Internal error: {e}", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    
    if demand_text_analysis is None:
        error_response = ErrorResponse(error="Could not analyze demand text", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    return demand_text_analysis


@router.post("/judicial_collection_demand_text_by_structured/", response_model=JudicialCollectionDemandTextAnalysis, dependencies=[Depends(get_api_key)])
async def judicial_collection_demand_text_by_structured_analyzer(
    input: JudicialCollectionDemandTextStructure = Form(..., description="Structured demand text to analyze"),
    control: JudicialCollectionDemandTextStructure | None = Form(None, description="Structured demand text to compare to"),
):
    try:
        analyzer = DemandTextAnalyzer()
        demand_text_analysis = analyzer.analyze_from_structured(input, control)
    except Exception as e:
        error_response = ErrorResponse(error=f"Internal error: {e}", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    
    if demand_text_analysis is None:
        error_response = ErrorResponse(error="Could not analyze demand text", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    return demand_text_analysis
