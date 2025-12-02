"""merge_migration_heads

Revision ID: 9e707763dda8
Revises: 7e9c79876662, ab12cd34ef56
Create Date: 2025-10-20 11:41:39.168839

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9e707763dda8'
down_revision: Union[str, None] = ('7e9c79876662', 'ab12cd34ef56')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
