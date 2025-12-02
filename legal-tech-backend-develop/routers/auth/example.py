from fastapi import Request
from . import router


@router.get("/example/user-info/")
async def get_user_info(request: Request):
    """
    Ejemplo de endpoint que muestra información del usuario autenticado.
    El middleware ya maneja la autenticación automáticamente.
    """
    from middleware.auth_middleware import get_current_user
    
    user = get_current_user(request)
    
    return {
        "message": f"Hola {user.name}!",
        "user_id": user.id,
        "role": user.role.value,
        "auth_type": "JWT User" if user.id else "Static Token",
        "active": user.active
    }


@router.get("/example/optional-auth/")
async def optional_auth_example(request: Request):
    """
    Ejemplo de endpoint con autenticación opcional.
    """
    from middleware.auth_middleware import get_current_user_optional
    
    user = get_current_user_optional(request)
    
    if user:
        return {
            "message": f"Hola {user.name}!",
            "authenticated": True,
            "user_id": user.id
        }
    else:
        return {
            "message": "Hola usuario anónimo!",
            "authenticated": False
        } 