from fastapi import HTTPException, Header

from services.auth import TokenService
from . import router


@router.post("/validate-token/")
async def validate_token(
    authorization: str | None = Header(None),
):
    """Handles the validation of user tokens."""
    if not authorization:
        raise HTTPException(status_code=400, detail="Authorization header missing")
    
    is_valid = TokenService.validate_token(authorization)
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    role = TokenService.get_role(authorization)
    
    return {"message": "Token is valid", "group": role.value if role else None}
