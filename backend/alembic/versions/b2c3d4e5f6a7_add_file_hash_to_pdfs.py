"""add_file_hash_to_pdfs

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-08-16 18:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add column allowing NULL initially to prevent errors on existing rows
    op.add_column('pdfs', sa.Column('file_hash', sa.String(), nullable=True))
    
    # 2. Backfill existing rows with a dummy hash so constraints pass
    # Since this is a simple backend we just generate a fake hash for old rows based on their uuid
    op.execute("UPDATE pdfs SET file_hash = md5(id::text)")
    
    # 3. Alter column to NOT NULL
    op.alter_column('pdfs', 'file_hash', nullable=False)
    
    # 4. Create the unique constraint
    op.create_unique_constraint('uq_pdfs_project_hash', 'pdfs', ['project_id', 'file_hash'])


def downgrade() -> None:
    op.drop_constraint('uq_pdfs_project_hash', 'pdfs', type_='unique')
    op.drop_column('pdfs', 'file_hash')
