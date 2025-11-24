from fastapi import File, Form, UploadFile

from models.api import error_response
from services.v2.document.demand_text import DemandTextAnalyzer, DemandTextAnalyzerInput, DemandTextAnalyzerOutput
from . import router


@router.post("/demand-text-from-file/", response_model=DemandTextAnalyzerOutput)
async def demand_text_file_post(
    input: UploadFile = File(..., description="PDF demand text file to analyze"),
    control: UploadFile = File(..., description="PDF demand text file to compare to"),
):
    """Handles the analysis of demand text files."""
    if input.content_type != "application/pdf":
        return error_response("Invalid input file type", 400)
    if control.content_type != "application/pdf":
        return error_response("Invalid control file type", 400)
    
    try:
        analyzer = DemandTextAnalyzer(input=DemandTextAnalyzerInput())
        demand_text_analysis = analyzer.analyze()
    except Exception as e:
        return error_response(f"Could not analyze demand text: {e}", 500)
    return demand_text_analysis


@router.post("/demand-text-from-mixed/", response_model=DemandTextAnalyzerOutput)
async def demand_text_mixed_post(
    input: DemandTextAnalyzerInput = Form(..., description="Structured demand text to analyze"),
    control: UploadFile = File(..., description="PDF demand text file to compare to"),
):
    """Handles the analysis of a demand text file and a generation result."""
    if control.content_type != "application/pdf":
        return error_response("Invalid control file type", 400)
    
    try:
        analyzer = DemandTextAnalyzer(input=input)
        demand_text_analysis = analyzer.analyze()
    except Exception as e:
        return error_response(f"Could not analyze demand text: {e}", 500)
    return demand_text_analysis


@router.post("/demand-text-from-structure/", response_model=DemandTextAnalyzerOutput)
async def demand_text_structure_post(
    input: DemandTextAnalyzerInput = Form(..., description="Structured demand text to analyze"),
    control: DemandTextAnalyzerInput | None = Form(None, description="Structured demand text to compare to"),
):
    """Handles the analysis of demand text generation results."""
    try:
        analyzer = DemandTextAnalyzer(input=input, control=control)
        demand_text_analysis = analyzer.analyze()
    except Exception as e:
        return error_response(f"Could not analyze demand text: {e}", 500)
    return demand_text_analysis
