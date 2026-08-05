"""add_guest_sessions_and_relationships

Revision ID: dae4df286721
Revises: 001_initial
Create Date: 2026-08-06 01:36:39.987679

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dae4df286721'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    from sqlalchemy.dialects import postgresql
    op.create_table('guest_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('guest_id', sa.String(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_guest_sessions_guest_id'), 'guest_sessions', ['guest_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_guest_sessions_guest_id'), table_name='guest_sessions')
    op.drop_table('guest_sessions')
