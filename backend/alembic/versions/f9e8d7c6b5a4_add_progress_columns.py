"""Add research run progress columns additive

Revision ID: f9e8d7c6b5a4
Revises: 4fcdd0ea1465
Create Date: 2026-08-22 17:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f9e8d7c6b5a4'
down_revision: Union[str, None] = '4fcdd0ea1465'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Explicitly additive migration for research_runs
    op.add_column('research_runs', sa.Column('project_id', sa.UUID(as_uuid=True), nullable=True))
    op.add_column('research_runs', sa.Column('user_id', sa.UUID(as_uuid=True), nullable=True))
    op.add_column('research_runs', sa.Column('mode', sa.String(), nullable=True))
    op.add_column('research_runs', sa.Column('steps_data', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=False))
    op.add_column('research_runs', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))

def downgrade() -> None:
    op.drop_column('research_runs', 'updated_at')
    op.drop_column('research_runs', 'steps_data')
    op.drop_column('research_runs', 'mode')
    op.drop_column('research_runs', 'user_id')
    op.drop_column('research_runs', 'project_id')
