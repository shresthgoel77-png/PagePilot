"""Convert parsed_text to JSONB

Revision ID: 849668814bb7
Revises: d4e5f6a7b8c9
Create Date: 2026-08-16 20:17:54.911738

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '849668814bb7'
down_revision: Union[str, None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Safely convert Text to JSONB wrapping raw strings
    op.execute("ALTER TABLE pdfs ALTER COLUMN parsed_text TYPE JSONB USING to_jsonb(parsed_text)")

def downgrade() -> None:
    # Safely convert JSONB back to Text
    op.execute("ALTER TABLE pdfs ALTER COLUMN parsed_text TYPE TEXT USING parsed_text::text")
