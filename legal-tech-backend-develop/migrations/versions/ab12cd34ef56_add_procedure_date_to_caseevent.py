"""add_procedure_date_to_caseevent

Revision ID: ab12cd34ef56
Revises: 56613d282ea8
Create Date: 2025-10-20 00:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ab12cd34ef56'
down_revision: Union[str, None] = '56613d282ea8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('caseevent', sa.Column('procedure_date', sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column('caseevent', 'procedure_date')


