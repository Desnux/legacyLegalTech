import json
import logging
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Form
from fastapi.responses import JSONResponse

from database.ext_db import get_session, Session
from models.pydantic import ErrorResponse
from services.network import EmailResponseGenerator, EmailService
from routers.base import get_api_key


router = APIRouter()


@router.post("/email/", dependencies=[Depends(get_api_key)])
async def email(
    subject: str = Form(..., description="Email subject"),
    from_email: str = Form(..., description="Email sender"),
    to_email: str = Form(..., description="Email desired receiver"),
    payload: str = Body(..., description="Email messsage payload"),
    thread_id: str = Form(..., description="Message thread ID"),
    message_id: str = Form(..., description="Message ID"),
    session: Session = Depends(get_session),
):
    payload_dict: dict = json.loads(payload)
    email_service = EmailService()

    from_list = list(map(lambda x: email_service.normalize_email(x), from_email.strip().split(",")))
    to_list = list(map(lambda x: x.strip(), to_email.strip().split(",")))
    if len(from_list) == 1:
        if email_service.assistant_local in from_list[0]:
            logging.info(f"Ignored email self event")
            return JSONResponse(status_code=200, content={"message": "Email successfully handled"})
    from_list = list(filter(lambda x: email_service.contains_whitelist_term(x) and not email_service.contains_blacklist_term(x), from_list))
    if len(from_list) == 0:
        logging.warning("No valid email addresses to respond to")
        return JSONResponse(status_code=200, content={"message": "Email successfully handled"})

    case_uuid: UUID | None = None
    for email in to_list:
        email_local, email_suffix, email_domain = email_service.extract_email_parts(email)
        if email_local == email_service.assistant_local and email_domain == email_service.assistant_domain and email_suffix:
            try:
                case_uuid = UUID(email_suffix)
            except ValueError:
                logging.warning(f"Invalid case UUID ({email_suffix})")
    if case_uuid:
        logging.info(f"Email event for case {case_uuid} ({subject})")
    else:
        logging.info(f"Email event without explicit case ({subject})")

    email_response_generator = EmailResponseGenerator(
        session,
        thread_id,
        message_id,
        f"{email_service.assistant_local}@{email_service.assistant_domain}",
        from_list,
        case_uuid,
    )
    try:
        response = email_response_generator.generate_response(payload_dict.get("text", ""))
    except Exception as e:
        logging.warning(f"Could not generate response to email: {e}")
        response = "No puedo atender su solicitud en este momento."
    
    if response is None:
        return JSONResponse(status_code=200, content={"message": "Email successfully handled"})

    try:
        email_service.respond(thread_id, message_id, response)
    except Exception as e:
        logging.warning(f"Could not respond to email: {e}")
        error_response = ErrorResponse(error=f"Internal error: {e}", code=500)
        return JSONResponse(status_code=500, content=error_response.model_dump())
    return JSONResponse(status_code=200, content={"message": "Email successfully handled"})
