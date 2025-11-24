from fastapi import Body

from models.api import error_response
from services.v2.document.withdrawal import (
    WithdrawalGenerator,
    WithdrawalGeneratorInput,
    WithdrawalGeneratorOutput,
)
from . import router


@router.post("/withdrawal-from-structure/", response_model=WithdrawalGeneratorOutput)
async def withdrawal_from_structure_post(
    input: WithdrawalGeneratorInput = Body(..., description="Withdrawal input as structured json"),
):
    """Handles the generation of a withdrawal from structured input."""
    try:
        withdrawal_generator = WithdrawalGenerator(input)
        structure = withdrawal_generator.generate()
    except Exception as e:
        return error_response(f"Could not generate withdrawal: {e}", 500, True)
    return structure
