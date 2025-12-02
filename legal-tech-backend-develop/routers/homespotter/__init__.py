from fastapi import APIRouter

router = APIRouter(
    prefix="/homespotter",
    tags=["HomeSpotter"],
)

# Import endpoints to register them with the router
from . import homespotter_controller  # noqa: E402, F401 