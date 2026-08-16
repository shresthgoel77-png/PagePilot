import asyncio
import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.models.ingestion_job import IngestionJob, JobStatus
from app.models.pdf import PDF, PDFStatus
from app.services import indexing_pipeline

logger = logging.getLogger("researchos.job_worker")

# Exponential backoff delays in seconds for each retry attempt
RETRY_DELAYS = [30, 120, 480]
POLL_INTERVAL_SECONDS = 2


async def claim_next_job(db: AsyncSession) -> IngestionJob | None:
    """Atomically claim the next eligible job using SELECT FOR UPDATE SKIP LOCKED."""
    now = datetime.now(timezone.utc)
    stmt = (
        select(IngestionJob)
        .where(
            (
                IngestionJob.status.in_([JobStatus.pending, JobStatus.retry]) &
                ((IngestionJob.next_retry_at <= now) | (IngestionJob.next_retry_at.is_(None)))
            ) |
            (
                (IngestionJob.status == JobStatus.processing) &
                (IngestionJob.locked_until < now)
            )
        )
        .order_by(IngestionJob.created_at.asc())
        .limit(1)
        .with_for_update(skip_locked=True)
    )
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if job:
        job.status = JobStatus.processing
        job.attempt_count += 1
        job.locked_until = now + timedelta(minutes=10)
        job.updated_at = now
        await db.commit()
        await db.refresh(job)

    return job


async def process_job(job: IngestionJob) -> None:
    """Run the indexing pipeline for a claimed job."""
    logger.info(f"Processing job {job.id} for pdf {job.pdf_id} (attempt {job.attempt_count})")

    async with AsyncSessionLocal() as db:
        try:
            await indexing_pipeline.run(
                project_id=job.project_id,
                file_path=job.file_path,
                user_id=job.user_id,
            )

            # Mark job completed
            job_stmt = (
                update(IngestionJob)
                .where(IngestionJob.id == job.id)
                .values(
                    status=JobStatus.completed,
                    updated_at=datetime.now(timezone.utc),
                    locked_until=None,
                    error_message=None,
                )
            )
            await db.execute(job_stmt)
            await db.commit()
            logger.info(f"Job {job.id} completed successfully")

        except Exception as e:
            logger.exception(f"Job {job.id} failed on attempt {job.attempt_count}: {e}")
            await _handle_failure(db, job, str(e))


async def _handle_failure(db: AsyncSession, job: IngestionJob, error_msg: str) -> None:
    """Handle a job failure: schedule retry or mark as permanently failed."""
    now = datetime.now(timezone.utc)

    if job.attempt_count < job.max_attempts:
        # Schedule retry with exponential backoff
        delay_idx = min(job.attempt_count - 1, len(RETRY_DELAYS) - 1)
        delay = RETRY_DELAYS[delay_idx]
        next_retry = now + timedelta(seconds=delay)

        stmt = (
            update(IngestionJob)
            .where(IngestionJob.id == job.id)
            .values(
                status=JobStatus.retry,
                next_retry_at=next_retry,
                locked_until=None,
                error_message=error_msg,
                updated_at=now,
            )
        )
        await db.execute(stmt)
        await db.commit()
        logger.info(f"Job {job.id} scheduled for retry at {next_retry} (attempt {job.attempt_count}/{job.max_attempts})")
    else:
        # Max attempts exhausted — mark as permanently failed
        stmt = (
            update(IngestionJob)
            .where(IngestionJob.id == job.id)
            .values(
                status=JobStatus.failed,
                error_message=error_msg,
                locked_until=None,
                updated_at=now,
            )
        )
        await db.execute(stmt)

        # Also mark the PDF as errored
        pdf_stmt = (
            update(PDF)
            .where(PDF.id == job.pdf_id)
            .values(
                status=PDFStatus.error,
                parsed_text=f"Ingestion failed after {job.max_attempts} attempts: {error_msg}",
            )
        )
        await db.execute(pdf_stmt)
        await db.commit()
        logger.error(f"Job {job.id} permanently failed after {job.max_attempts} attempts")


async def worker_loop(shutdown_event: asyncio.Event) -> None:
    """Main worker loop — polls for jobs until shutdown is signalled."""
    logger.info("Ingestion job worker started")

    while not shutdown_event.is_set():
        try:
            async with AsyncSessionLocal() as db:
                job = await claim_next_job(db)

            if job:
                await process_job(job)
            else:
                # No jobs available — wait before polling again
                try:
                    await asyncio.wait_for(shutdown_event.wait(), timeout=POLL_INTERVAL_SECONDS)
                except asyncio.TimeoutError:
                    pass  # Normal timeout, just poll again

        except Exception as e:
            logger.exception(f"Worker loop encountered an unexpected error: {e}")
            # Avoid tight retry loops on infrastructure failures
            await asyncio.sleep(5)

    logger.info("Ingestion job worker shutting down")



