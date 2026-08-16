from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class PDFResponse(BaseModel):
    id: UUID
    project_id: UUID
    filename: str
    original_name: str
    status: str
    created_at: datetime
    page_count: Optional[int] = None
    
    error_message: Optional[str] = None
    progress: Optional[int] = 0
    job_id: Optional[UUID] = None
    indexed_at: Optional[datetime] = None

    # Enables SQLAlchemy parsing accurately across Pydantic abstractions natively without serialization conflicts 
    class Config:
        from_attributes = True
