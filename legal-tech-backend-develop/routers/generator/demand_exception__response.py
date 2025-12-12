from fastapi import Body
from models.api import error_response
from models.pydantic import (
    LegalExceptionResponse,
    LegalExceptionResponseInput,
)
from services.generator.demand_exception_response_generator import (
    DemandExceptionResponseGenerator,
)
from services.v2.document.demand_exception import DemandExceptionInformation
from services.v2.document.demand_text import DemandTextStructure
from . import router


@router.post(
    "/demand-exception-response/",
    response_model=LegalExceptionResponse,
    summary="Evacúa traslado y responde excepciones como demandante",
)
async def generate_demand_exception_response(
    input: LegalExceptionResponseInput = Body(
        ...,
        description="Información del caso, partes, abogados y solicitudes secundarias",
    ),
    demand_exception: DemandExceptionInformation = Body(
        ...,
        description="Excepciones opuestas por el demandado",
    ),
    demand_text: DemandTextStructure = Body(
        ...,
        description="Texto estructurado de la demanda original",
    ),
):
    """
    Genera un escrito del DEMANDANTE que evacúa traslado
    y responde las excepciones opuestas por el demandado.
    """
    try:
        generator = DemandExceptionResponseGenerator(input)
        response = generator.generate(
            demand_exception=demand_exception,
            demand_text=demand_text,
        )
    except Exception as e:
        return error_response(f"Internal error: {e}", 500)

    return response
