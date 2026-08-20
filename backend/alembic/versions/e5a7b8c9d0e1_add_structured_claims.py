"""add structured claims

Revision ID: e5a7b8c9d0e1
Revises: 849668814bb7
Create Date: 2026-08-20 20:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e5a7b8c9d0e1'
down_revision = '849668814bb7'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column('chat_messages', sa.Column('structured_claims', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('chat_messages', sa.Column('verification_status', sa.String(), nullable=True))
    op.add_column('chat_messages', sa.Column('verification_timestamp', sa.DateTime(timezone=True), nullable=True))

def downgrade() -> None:
    op.drop_column('chat_messages', 'verification_timestamp')
    op.drop_column('chat_messages', 'verification_status')
    op.drop_column('chat_messages', 'structured_claims')
