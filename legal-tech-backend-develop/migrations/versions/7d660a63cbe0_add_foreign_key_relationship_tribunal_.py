"""add_foreign_key_relationship_tribunal_court

Revision ID: 7d660a63cbe0
Revises: 950a4dba84ad
Create Date: 2025-09-22 16:13:03.942461

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '7d660a63cbe0'
down_revision: Union[str, None] = '950a4dba84ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add foreign key relationship between tribunal and court
    # First add the column as nullable
    op.add_column('tribunal', sa.Column('court_id', sa.Uuid(), nullable=True))
    
    # Update existing records with a default court_id (you may need to adjust this)
    # For now, we'll set them to NULL and let the application handle it
    # op.execute("UPDATE tribunal SET court_id = (SELECT id FROM court LIMIT 1) WHERE court_id IS NULL")
    
    # Create the foreign key constraint
    op.create_foreign_key('fk_tribunal_court_id', 'tribunal', 'court', ['court_id'], ['id'])


def downgrade() -> None:
    # Remove foreign key relationship between tribunal and court
    op.drop_constraint('fk_tribunal_court_id', 'tribunal', type_='foreignkey')
    op.drop_column('tribunal', 'court_id')
