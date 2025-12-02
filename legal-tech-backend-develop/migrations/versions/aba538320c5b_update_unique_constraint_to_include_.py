"""update_unique_constraint_to_include_procedure_description

Revision ID: aba538320c5b
Revises: e0484a317455
Create Date: 2025-09-12 00:36:15.297202

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aba538320c5b'
down_revision: Union[str, None] = 'e0484a317455'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the existing unique constraint
    op.drop_constraint('uq_folio_case_year', 'pjud_folios', type_='unique')
    
    # Create new unique constraint that includes procedure_description
    op.create_unique_constraint(
        'uq_folio_case_year_description', 
        'pjud_folios', 
        ['folio_number', 'case_number', 'year', 'procedure_description']
    )


def downgrade() -> None:
    # Drop the new unique constraint
    op.drop_constraint('uq_folio_case_year_description', 'pjud_folios', type_='unique')
    
    # Restore the original unique constraint
    op.create_unique_constraint(
        'uq_folio_case_year', 
        'pjud_folios', 
        ['folio_number', 'case_number', 'year']
    )
