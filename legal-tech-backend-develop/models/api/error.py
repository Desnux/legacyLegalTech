import logging
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Error response structure."""
    error: str = Field(..., description="Error description")
    code: int = Field(..., description="Error code")


def error_response(error: str, code: int = 500, log: bool = False) -> JSONResponse:
    """Generate a structured JSON error response."""
    if log:
        logging.warning(error)
    error_model = ErrorResponse(error=error, code=code)
    return JSONResponse(status_code=code, content=error_model.model_dump())
