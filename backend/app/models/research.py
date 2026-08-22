import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base import Base

class ResearchRun(Base):
    __tablename__ = "research_runs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(UUID(as_uuid=True), nullable=True) # additive
    user_id = Column(UUID(as_uuid=True), nullable=True) # additive
    mode = Column(String, nullable=True) # additive
    
    query = Column(String, nullable=False)
    status = Column(String, default="planning", nullable=False)
    
    steps_data = Column(JSONB, default=list, nullable=False) # Maps to steps/artifacts (JSON) array functionally
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
