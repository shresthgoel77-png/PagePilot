"""add_locked_until_to_jobs

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-08-16 18:25:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('ingestion_jobs', sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f('ix_ingestion_jobs_locked_until'), 'ingestion_jobs', ['locked_until'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_ingestion_jobs_locked_until'), table_name='ingestion_jobs')
    op.drop_column('ingestion_jobs', 'locked_until')
