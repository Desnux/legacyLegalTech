"""add_notification_and_translation_evacuation_to_caseeventtype_enum

Revision ID: 56613d282ea8
Revises: af39c99359bf
Create Date: 2025-10-17 02:13:03.410335

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '56613d282ea8'
down_revision: Union[str, None] = 'af39c99359bf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Agregar NOTIFICATION al enum caseeventtype (en mayúsculas)
    op.execute("ALTER TYPE caseeventtype ADD VALUE 'NOTIFICATION'")
    
    # Agregar TRANSLATION_EVACUATION al enum caseeventtype (en mayúsculas)
    op.execute("ALTER TYPE caseeventtype ADD VALUE 'TRANSLATION_EVACUATION'")


def downgrade() -> None:
    # PostgreSQL no permite eliminar valores de enum directamente
    # Esta migración es solo aditiva
    pass
