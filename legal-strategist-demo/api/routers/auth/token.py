from fastapi import APIRouter, HTTPException, Header

from services.auth import TokenService


router = APIRouter()


@router.post("/validate-token")
async def validate_token(
    authorization: str | None = Header(None)
):
    if not authorization:
        raise HTTPException(status_code=400, detail="Authorization header missing")
    
    is_valid = TokenService.validate_token(authorization)
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {"message": "Token is valid"}
