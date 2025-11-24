"""add_trial_start_to_caseeventtype_enum

Revision ID: 31cf3da2255
Revises: 49d86797ea4e
Create Date: 2025-01-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '31cf3da2255'
down_revision: Union[str, None] = '49d86797ea4e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Agregar TRIAL_START al enum caseeventtype
    op.execute("ALTER TYPE caseeventtype ADD VALUE 'TRIAL_START'")


def downgrade() -> None:
    # PostgreSQL no permite eliminar valores de enum directamente
    # Esta migración es solo aditiva
    pass
