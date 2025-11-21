from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader

from config import Config
from models.api import ErrorResponse


api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


def get_api_key(api_key_header: str | None = Security(api_key_header)) -> str | None:
    """Validates and returns the API key header of a request."""
    if api_key_header in [f"Bearer {Config.AUTH_TOKEN}", f"Bearer {Config.IN_HOUSE_SUITE_TOKEN}"]:
        return api_key_header
    
    error_response = ErrorResponse(error="No se pudieron validar las credenciales", code=401)
    raise HTTPException(status_code=401, detail=error_response.model_dump())
