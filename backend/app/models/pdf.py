import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Enum, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base

class PDFStatus(str, enum.Enum):
    uploaded = "uploaded"
    queued = "queued"
    parsing = "parsing"
    ocr = "ocr"
    embedding = "embedding"
    indexing = "indexing"
    ready = "ready"
    error = "error"

class PDF(Base):
    __tablename__ = "pdfs"
    __table_args__ = (
        UniqueConstraint("project_id", "file_hash", name="uq_pdfs_project_hash"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False)
    filename = Column(String, nullable=False)
    original_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_hash = Column(String, nullable=False)
    page_count = Column(Integer, default=0)
    parsed_text = Column(Text, nullable=True)
    status = Column(Enum(PDFStatus), default=PDFStatus.uploaded, nullable=False)
    
    # New state tracking columns
    error_message = Column(Text, nullable=True)
    progress = Column(Integer, default=0, nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey('ingestion_jobs.id', ondelete='SET NULL'), nullable=True)
    indexed_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="pdfs")
