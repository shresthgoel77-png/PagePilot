"""add_pdf_status_fields

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-08-16 19:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add new columns
    op.add_column('pdfs', sa.Column('error_message', sa.Text(), nullable=True))
    op.add_column('pdfs', sa.Column('progress', sa.Integer(), server_default='0', nullable=False))
    op.add_column('pdfs', sa.Column('job_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('pdfs', sa.Column('indexed_at', sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key('fk_pdfs_job_id', 'pdfs', 'ingestion_jobs', ['job_id'], ['id'], ondelete='SET NULL')

    # 2. Safely recreate ENUM to ensure 100% reversibility mapping
    op.execute("ALTER TYPE pdfstatus RENAME TO pdfstatus_old")
    op.execute("CREATE TYPE pdfstatus AS ENUM('uploaded', 'queued', 'parsing', 'ocr', 'embedding', 'indexing', 'ready', 'error')")
    op.execute("ALTER TABLE pdfs ALTER COLUMN status TYPE pdfstatus USING status::text::pdfstatus")
    op.execute("DROP TYPE pdfstatus_old")


def downgrade() -> None:
    # 1. Drop constraints and columns
    op.drop_constraint('fk_pdfs_job_id', 'pdfs', type_='foreignkey')
    op.drop_column('pdfs', 'indexed_at')
    op.drop_column('pdfs', 'job_id')
    op.drop_column('pdfs', 'progress')
    op.drop_column('pdfs', 'error_message')

    # 2. Safely revert ENUM mapping backing down extended values natively
    op.execute("UPDATE pdfs SET status = 'uploaded' WHERE status NOT IN ('uploaded', 'parsing', 'parsed', 'error')")
    op.execute("UPDATE pdfs SET status = 'parsed' WHERE status = 'ready'")
    
    op.execute("ALTER TYPE pdfstatus RENAME TO pdfstatus_new")
    op.execute("CREATE TYPE pdfstatus AS ENUM('uploaded', 'parsing', 'parsed', 'error')")
    op.execute("ALTER TABLE pdfs ALTER COLUMN status TYPE pdfstatus USING status::text::pdfstatus")
    op.execute("DROP TYPE pdfstatus_new")
