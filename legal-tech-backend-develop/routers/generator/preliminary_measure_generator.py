import base64
import logging
from datetime import date
from fastapi import Body, Response, File, Form, UploadFile

from models.api import error_response
from services.v2.document.preliminary_measure import (
    PreliminaryMeasureGenerator,
    PreliminaryMeasureGeneratorInput,
)
from services.v2.document.preliminary_measure.input import (
    PreliminaryMeasureInputExtractor,
    PreliminaryMeasureInputExtractorInput,
)
from . import router


@router.post(
    "/preliminary-measure-from-raw-text/",
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "Returns a generated PDF file",
        }
    },
    response_class=Response,
)
async def preliminary_measure_from_raw_text_post(
    local_police_number: int | None = Form(None, description="Local police station number, if any"),
    communication_date: date = Form(..., description="Communication to the client date"),
    file: UploadFile = File(..., description="COOPEUCH report PDF file", media_type="application/pdf"),
    coopeuch_registry_image: UploadFile | None = File(None, description="COOPEUCH registry image", media_type=["image/png", "image/jpeg"]),
    transaction_to_self_image: UploadFile | None = File(None, description="Transaction to self account image", media_type=["image/png", "image/jpeg"]),
    payment_to_account_image: UploadFile | None = File(None, description="Payment to user account image", media_type=["image/png", "image/jpeg"]),
    user_report_image: UploadFile | None = File(None, description="User report image", media_type=["image/png", "image/jpeg"]),
    safesigner_report_image: UploadFile | None = File(None, description="Safesigner report image", media_type=["image/png", "image/jpeg"]),
    mastercard_connect_report_image: UploadFile | None = File(None, description="Mastercard Connect report image", media_type=["image/png", "image/jpeg"]),
    celmedia_report_image: UploadFile | None = File(None, description="CELMEDIA report image", media_type=["image/png", "image/jpeg"]),
):
    """Handles the generation of a preliminary measure from raw text."""
    coopeuch_registry_uri = None
    if coopeuch_registry_image:
        coopeuch_registry_bytes = await coopeuch_registry_image.read()
        coopeuch_registry_uri = (
            f"data:{coopeuch_registry_image.content_type};base64,"
            + base64.b64encode(coopeuch_registry_bytes).decode("utf-8")
        )
    
    transaction_to_self_uri = None
    if transaction_to_self_image:
        transaction_to_self_bytes = await transaction_to_self_image.read()
        transaction_to_self_uri = (
            f"data:{transaction_to_self_image.content_type};base64,"
            + base64.b64encode(transaction_to_self_bytes).decode("utf-8")
        )

    payment_to_account_uri = None
    if payment_to_account_image:
        payment_to_account_bytes = await payment_to_account_image.read()
        payment_to_account_uri = (
            f"data:{payment_to_account_image.content_type};base64,"
            + base64.b64encode(payment_to_account_bytes).decode("utf-8")
        )
    
    user_report_uri = None
    if user_report_image:
        user_report_bytes = await user_report_image.read()
        user_report_uri = (
            f"data:{user_report_image.content_type};base64,"
            + base64.b64encode(user_report_bytes).decode("utf-8")
        )

    safesigner_report_uri = None
    if safesigner_report_image:
        safesigner_report_bytes = await safesigner_report_image.read()
        safesigner_report_uri = (
            f"data:{safesigner_report_image.content_type};base64,"
            + base64.b64encode(safesigner_report_bytes).decode("utf-8")
        )
    
    mastercard_connect_report_uri = None
    if mastercard_connect_report_image:
        mastercard_connect_report_bytes = await mastercard_connect_report_image.read()
        mastercard_connect_report_uri = (
            f"data:{mastercard_connect_report_image.content_type};base64,"
            + base64.b64encode(mastercard_connect_report_bytes).decode("utf-8")
        )
    
    celmedia_report_uri = None
    if celmedia_report_image:
        celmedia_report_bytes = await celmedia_report_image.read()
        celmedia_report_uri = (
            f"data:{celmedia_report_image.content_type};base64,"
            + base64.b64encode(celmedia_report_bytes).decode("utf-8")
        )

    try:
        preliminary_measure_input_extractor = PreliminaryMeasureInputExtractor(PreliminaryMeasureInputExtractorInput(
            file=file,
            local_police_number=local_police_number,
            communication_date=communication_date,
            coopeuch_registry_uri=coopeuch_registry_uri,
            transaction_to_self_uri=transaction_to_self_uri,
            payment_to_account_uri=payment_to_account_uri,
            user_report_uri=user_report_uri,
            safesigner_report_uri=safesigner_report_uri,
            mastercard_connect_report_uri=mastercard_connect_report_uri,
            celmedia_report_uri=celmedia_report_uri,
        ))
        information = preliminary_measure_input_extractor.extract()
        logging.info(f"Preliminary measure input extractor metrics: {information.metrics.model_dump_json()}")
    except Exception as e:
        return error_response(f"Could not extract information from input: {e}", 500, True)
    if not information.structured_output:
        return error_response(f"Could not extract information from input", 500)
    
    try:
        preliminary_measure_generator = PreliminaryMeasureGenerator(PreliminaryMeasureGeneratorInput(
            **information.structured_output.model_dump(),
        ))
        preliminary_measure = preliminary_measure_generator.generate()
    except Exception as e:
        return error_response(f"Could not generate preliminary measure: {e}", 500, True)
    if preliminary_measure is None:
        return error_response("Could not generate preliminary measure", 500)
    return Response(
        content=preliminary_measure.pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=medida_prejudicial.pdf"},
    )


@router.post(
    "/preliminary-measure-from-structure/",
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "Returns a generated PDF file",
        }
    },
    response_class=Response,
)
async def preliminary_measure_from_structure_post(
    input: PreliminaryMeasureGeneratorInput = Body(..., description="Required information"),
):
    """Handles the generation of a preliminary measure from structured input."""
    try:
        generator = PreliminaryMeasureGenerator(input)
        preliminary_measure = generator.generate()
    except Exception as e:
        return error_response(f"Could not generate preliminary measure: {e}", 500, True)
    
    if preliminary_measure is None:
        return error_response("Could not generate preliminary measure", 500)
    return Response(
        content=preliminary_measure.pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                'attachment; '
                'filename="Medida Prejudicial.pdf"; '
                "filename*=UTF-8''Medida%20Prejudicial.pdf"
            )
        },
    )
