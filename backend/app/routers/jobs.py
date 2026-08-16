import logging
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.user import User
from app.models.ingestion_job import IngestionJob
from app.core.clerk_auth import get_current_user_clerk
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

logger = logging.getLogger("researchos.jobs")

router = APIRouter(prefix="/jobs", tags=["jobs"])


class JobStatusResponse(BaseModel):
    id: UUID
    pdf_id: UUID
    project_id: UUID
    status: str
    attempt_count: int
    max_attempts: int
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: UUID,
    current_user: User = Depends(get_current_user_clerk),
    db: AsyncSession = Depends(get_db),
):
    """Poll the status of an ingestion job."""
    stmt = select(IngestionJob).where(
        IngestionJob.id == job_id,
        IngestionJob.user_id == current_user.id,
    )
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse.model_validate(job)
