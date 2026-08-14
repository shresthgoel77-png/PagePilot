"""clerk_auth

Revision ID: 23014e913938
Revises: dae4df286721
Create Date: 2026-08-07 00:00:51.278817

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '23014e913938'
down_revision: Union[str, None] = 'dae4df286721'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add column as nullable first
    op.add_column('users', sa.Column('clerk_id', sa.String(), nullable=True))
    # Delete orphaned users from previous auth system before enforcing NOT NULL
    op.execute("DELETE FROM users WHERE clerk_id IS NULL")
    # Enforce NOT NULL and add index
    op.alter_column('users', 'clerk_id', nullable=False)
    op.create_index(op.f('ix_users_clerk_id'), 'users', ['clerk_id'], unique=True)
    # Drop old legacy columns
    op.drop_column('users', 'hashed_password')
    op.drop_column('users', 'is_guest')


def downgrade() -> None:
    op.add_column('users', sa.Column('is_guest', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False))
    op.add_column('users', sa.Column('hashed_password', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_index(op.f('ix_users_clerk_id'), table_name='users')
    op.drop_column('users', 'clerk_id')
