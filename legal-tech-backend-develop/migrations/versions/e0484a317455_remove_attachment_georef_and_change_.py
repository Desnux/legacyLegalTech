"""remove_attachment_georef_and_change_types

Revision ID: e0484a317455
Revises: 2705da507b9c
Create Date: 2025-09-12 00:11:41.309173

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e0484a317455'
down_revision: Union[str, None] = '2705da507b9c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # First, clear the table to avoid data type conflicts
    op.execute("DELETE FROM pjud_folios")
    
    # Drop the unique constraint first
    op.drop_constraint('uq_folio_rol_year', 'pjud_folios', type_='unique')
    
    # Remove columns that are no longer needed
    op.drop_column('pjud_folios', 'anexo')
    op.drop_column('pjud_folios', 'georref')
    
    # Change column types using USING clause for PostgreSQL
    op.execute('ALTER TABLE pjud_folios ALTER COLUMN folio TYPE INTEGER USING folio::integer')
    op.execute('ALTER TABLE pjud_folios ALTER COLUMN year TYPE INTEGER USING year::integer')
    op.execute('ALTER TABLE pjud_folios ALTER COLUMN foja TYPE INTEGER USING foja::integer')
    
    # Rename columns to match new model
    op.alter_column('pjud_folios', 'folio', new_column_name='folio_number')
    op.alter_column('pjud_folios', 'rol', new_column_name='case_number')
    op.alter_column('pjud_folios', 'doc', new_column_name='document')
    op.alter_column('pjud_folios', 'etapa', new_column_name='stage')
    op.alter_column('pjud_folios', 'tramite', new_column_name='procedure')
    op.alter_column('pjud_folios', 'desc_tramite', new_column_name='procedure_description')
    op.alter_column('pjud_folios', 'fec_tramite', new_column_name='procedure_date')
    op.alter_column('pjud_folios', 'foja', new_column_name='page')
    op.alter_column('pjud_folios', 'hito', new_column_name='milestone')
    
    # Change procedure_date to Date type using USING clause
    op.execute('ALTER TABLE pjud_folios ALTER COLUMN procedure_date TYPE DATE USING procedure_date::date')
    
    # Add new unique constraint with new column names
    op.create_unique_constraint('uq_folio_case_year', 'pjud_folios', ['folio_number', 'case_number', 'year'])


def downgrade() -> None:
    # Drop the new unique constraint
    op.drop_constraint('uq_folio_case_year', 'pjud_folios', type_='unique')
    
    # Rename columns back to original names
    op.alter_column('pjud_folios', 'folio_number', new_column_name='folio')
    op.alter_column('pjud_folios', 'case_number', new_column_name='rol')
    op.alter_column('pjud_folios', 'document', new_column_name='doc')
    op.alter_column('pjud_folios', 'stage', new_column_name='etapa')
    op.alter_column('pjud_folios', 'procedure', new_column_name='tramite')
    op.alter_column('pjud_folios', 'procedure_description', new_column_name='desc_tramite')
    op.alter_column('pjud_folios', 'procedure_date', new_column_name='fec_tramite')
    op.alter_column('pjud_folios', 'page', new_column_name='foja')
    op.alter_column('pjud_folios', 'milestone', new_column_name='hito')
    
    # Change column types back to String using USING clause
    op.execute('ALTER TABLE pjud_folios ALTER COLUMN folio TYPE VARCHAR(50) USING folio::text')
    op.execute('ALTER TABLE pjud_folios ALTER COLUMN year TYPE VARCHAR(4) USING year::text')
    op.execute('ALTER TABLE pjud_folios ALTER COLUMN foja TYPE VARCHAR(20) USING foja::text')
    
    op.execute('ALTER TABLE pjud_folios ALTER COLUMN fec_tramite TYPE VARCHAR(50) USING fec_tramite::text')
    
    # Add back the removed columns
    op.add_column('pjud_folios', sa.Column('anexo', sa.Text(), nullable=True))
    op.add_column('pjud_folios', sa.Column('georref', sa.String(50), nullable=True))
    
    # Add back the original unique constraint
    op.create_unique_constraint('uq_folio_rol_year', 'pjud_folios', ['folio', 'rol', 'year'])
