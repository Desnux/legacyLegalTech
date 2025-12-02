"""update_court_and_tribunal_models_add_code_field

Revision ID: 950a4dba84ad
Revises: 4682a2444df1
Create Date: 2025-09-22 15:29:44.594849

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '950a4dba84ad'
down_revision: Union[str, None] = '4682a2444df1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add code column to court table with default value first
    op.add_column('court', sa.Column('code', sa.Integer(), nullable=True))
    
    # Update existing records with a default code value
    op.execute("UPDATE court SET code = 0 WHERE code IS NULL")
    
    # Now make the column NOT NULL
    op.alter_column('court', 'code', nullable=False)
    
    # Add code column to tribunal table with default value first
    op.add_column('tribunal', sa.Column('code', sa.Integer(), nullable=True))
    
    # Update existing records with a default code value
    op.execute("UPDATE tribunal SET code = 0 WHERE code IS NULL")
    
    # Now make the column NOT NULL
    op.alter_column('tribunal', 'code', nullable=False)
    
    # Remove city column from court table (if it exists)
    # Note: This might fail if the column doesn't exist, which is fine
    try:
        op.drop_column('court', 'city')
    except Exception:
        pass  # Column might not exist, ignore the error


def downgrade() -> None:
    # Remove code column from tribunal table
    op.drop_column('tribunal', 'code')
    
    # Remove code column from court table
    op.drop_column('court', 'code')
    
    # Add back city column to court table
    op.add_column('court', sa.Column('city', sa.String(), nullable=False))
