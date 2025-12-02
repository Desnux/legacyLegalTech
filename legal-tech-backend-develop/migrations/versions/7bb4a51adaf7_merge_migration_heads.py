"""merge_migration_heads

Revision ID: 7bb4a51adaf7
Revises: aba538320c5b, eb1849003916
Create Date: 2025-09-12 11:19:22.727533

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7bb4a51adaf7'
down_revision: Union[str, None] = ('aba538320c5b', 'eb1849003916')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
