import logging
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.user import User
from app.models.ingestion_job import IngestionJob, JobStatus
from app.core.clerk_auth import get_current_user_clerk
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from sqlalchemy import func

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


class JobMonitoringResponse(BaseModel):
    queue_depth: int
    in_progress: int
    average_processing_seconds: float
    recent_failures: List[JobStatusResponse]


@router.get("/monitoring", response_model=JobMonitoringResponse)
async def get_jobs_monitoring(
    current_user: User = Depends(get_current_user_clerk),
    db: AsyncSession = Depends(get_db),
):
    """Admin dashboard monitoring metrics for ingestion jobs natively mapping securely."""
    
    # 1. Queue depth
    queue_stmt = select(func.count(IngestionJob.id)).where(IngestionJob.status == JobStatus.pending)
    queue_result = await db.execute(queue_stmt)
    queue_depth = queue_result.scalar_one() or 0
    
    # 2. In progress
    progress_stmt = select(func.count(IngestionJob.id)).where(IngestionJob.status == JobStatus.processing)
    progress_result = await db.execute(progress_stmt)
    in_progress = progress_result.scalar_one() or 0
    
    # 3. Average processing time
    avg_stmt = select(func.avg(
        func.extract('epoch', IngestionJob.updated_at) - func.extract('epoch', IngestionJob.created_at)
    )).where(IngestionJob.status == JobStatus.completed)
    avg_result = await db.execute(avg_stmt)
    avg_processing = avg_result.scalar_one() or 0.0
    
    # 4. Recent Failures
    fail_stmt = select(IngestionJob).where(IngestionJob.status == JobStatus.failed).order_by(IngestionJob.updated_at.desc()).limit(10)
    fail_result = await db.execute(fail_stmt)
    failures = fail_result.scalars().all()
    
    return JobMonitoringResponse(
        queue_depth=queue_depth,
        in_progress=in_progress,
        average_processing_seconds=float(avg_processing),
        recent_failures=[JobStatusResponse.model_validate(f) for f in failures]
    )

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
