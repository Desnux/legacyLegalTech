import asyncio
import logging
from fastapi import Body, Depends, File, UploadFile

from database.ext_db import Session
from models.api import error_response
from models.pydantic import AnnexFile, PJUDDDO, PJUDLegalRepresentative
from services.extractor import AddressExtractor
from services.pjud import PJUDController
from services.tracker import CaseTracker
from services.v2.document.demand_text import DemandTextSenderInput, DemandTextSendResponse
from middleware.auth_middleware import get_current_session
from . import router


ALLOWED_FILE_TYPE = "application/pdf"
MAX_RETRIES = 3


async def simulate_pjud_scraping() -> DemandTextSendResponse:
    """Simulates PJUD scraping with an artificial delay."""
    await asyncio.sleep(10)
    return DemandTextSendResponse(message="Valid", status=200)


@router.post("/demand-text/", response_model=DemandTextSendResponse)
async def demand_text(
    input: DemandTextSenderInput = Body(..., description="PJUD data"),
    demand_text: UploadFile = File(..., description="Demand text PDF file"),
    contract: UploadFile | None = File(None, description="Contract PDF file"),
    mandate: UploadFile = File(..., description="Lawyer mandate PDF file"),
    session: Session = Depends(get_current_session),
    extra_files: list[UploadFile] = File([], description="Additional PDF files", max_length=20),
    extra_files_labels: list[str] = File([], description="Additional PDF files labels", max_length=20),
    address_extractor: AddressExtractor = Depends(),
    controller: PJUDController = Depends(),
    tracker: CaseTracker = Depends(),
):
    """Handles the submission of a demand text and related documents to PJUD."""
    for file, name in [(demand_text, "demand text"), (mandate, "mandate")]:
        if file.content_type != ALLOWED_FILE_TYPE:
            return error_response(f"Invalid {name} file type", 400)
    
    if contract is not None and contract.content_type != ALLOWED_FILE_TYPE:
        return error_response("Invalid contract file type", 400)

    for file in extra_files:
        if file.content_type != ALLOWED_FILE_TYPE:
            return error_response(f"Invalid annex file type", 400)
    
    annexes = []
    if contract is not None:
        annexes.append(AnnexFile(label="Contrato", upload_file=contract))
    annexes.append(AnnexFile(label="Mandato", upload_file=mandate))
    annexes.extend(
        AnnexFile(label=label, upload_file=file)
        for label, file in zip(extra_files_labels, extra_files)
    )

    defendants: list[PJUDDDO] = []
    try:
        for defendant in input.information.defendants or []:
            pjud_ddo = PJUDDDO(
                raw_address=defendant.address or "",
                raw_name=defendant.name or "",
                identifier=defendant.identifier or "",
                legal_representatives=[
                    PJUDLegalRepresentative(raw_name=representative.name or "", identifier=representative.identifier or "")
                    for representative in defendant.legal_representatives or []
                ],
                addresses=[address_extractor.extract_from_text(defendant.address)] if defendant.address else [],
            )
            defendants.append(pjud_ddo)
    except Exception as e:
        return error_response(f"Invalid or incomplete defendant address: {e}", 400, True)

    controller_response = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            if input.debug:
                controller_response = await simulate_pjud_scraping()
            else:
                controller_response = await controller.send_demand_to_pjud(input, demand_text, defendants, annexes)
            if controller_response:
                break
        except Exception as e:
            logging.warning(f"Attempt {attempt}/{MAX_RETRIES} to send demand text failed: {e}")
            if attempt == MAX_RETRIES:
                return error_response(f"Internal error: {e}", 500)
    
    if not controller_response:
        return error_response(f"Could not send demand text after {MAX_RETRIES} retries", 500)
    
    case_id = None
    try:
        created_case = tracker.create_case_from_demand_text(session, input.information, input.structure, annexes, input.debug)
        if created_case:
            case_id = created_case.id
    except Exception as e:
        logging.warning(f"Could not create case from demand text: {e}")
    
    return DemandTextSendResponse(
        message=controller_response.message,
        status=controller_response.status,
        case_id=case_id,
    )
