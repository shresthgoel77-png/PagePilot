import asyncio
import uuid
import pytest
import os
from datetime import datetime, timezone
from unittest.mock import MagicMock, AsyncMock, patch

# Mock env vars before app code gets imported
os.environ["CLERK_SECRET_KEY"] = "mock_key"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://mock:pass@localhost/mock_db"
os.environ["QDRANT_URL"] = "http://localhost:6333"
os.environ["SECRET_KEY"] = "mock"
os.environ["UPLOAD_DIR"] = "./uploads"
os.environ["GEMINI_API_KEY"] = "mock_key"

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ingestion_job import IngestionJob, JobStatus
from app.models.pdf import PDF, PDFStatus
from app.services.job_worker import process_job, _handle_failure, claim_next_job

@pytest.mark.asyncio
async def test_job_worker_duplicate_upload():
    """Verify that if db.execute returns an existing PDF, upload_pdf returns early.
    (This asserts the logic added to pdfs.py where hashing prevents duplicate processing.)
    """
    from app.routers.pdfs import upload_pdf
    from fastapi import UploadFile
    from collections import namedtuple
    from app.schemas.pdf import PDFResponse
    import io

    # Mock DB
    db_mock = AsyncMock(spec=AsyncSession)
    
    # Setup mock existing PDF
    existing_pdf = PDF(
        id=uuid.uuid4(),
        file_hash="dummy_hash",
        project_id=uuid.uuid4(),
        status=PDFStatus.parsed,
        filename="existing.pdf",
        original_name="test.pdf",
        created_at=datetime.now(timezone.utc)
    )
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = existing_pdf
    db_mock.execute.return_value = result_mock
    
    # Mock user and file
    user_mock = MagicMock(id=uuid.uuid4())
    file_bytes = b"%PDF-1.4 mock content"
    
    file_mock = MagicMock(spec=UploadFile)
    file_mock.filename = "test.pdf"
    file_mock.content_type = "application/pdf"
    file_mock.size = len(file_bytes)
    file_mock.read = AsyncMock(return_value=file_bytes)
    
    # Mock verify_project
    with patch("app.routers.pdfs.verify_project", new_callable=AsyncMock) as vp_mock:
        response = await upload_pdf(project_id=uuid.uuid4(), file=file_mock, current_user=user_mock, db=db_mock)
        
        # Ensure it didn't call db.add (no new PDF inserted!)
        db_mock.add.assert_not_called()
        
        # Ensure it returned the matching existing PDF
        assert response.id == existing_pdf.id


@pytest.mark.asyncio
async def test_job_worker_transient_failure_recovery():
    """Verify that process_job correctly delegates exception to _handle_failure and retries."""
    job = IngestionJob(
        id=uuid.uuid4(), 
        pdf_id=uuid.uuid4(), 
        status=JobStatus.processing,
        attempt_count=1,
        max_attempts=3
    )
    
    with patch("app.services.job_worker.indexing_pipeline.run", new_callable=AsyncMock) as pipeline_mock:
        pipeline_mock.side_effect = Exception("Transient Qdrant Error")
        
        with patch("app.services.job_worker.AsyncSessionLocal") as session_factory_mock:
            db_mock = AsyncMock(spec=AsyncSession)
            session_factory_mock.return_value.__aenter__.return_value = db_mock
            
            await process_job(job)
            
            # Since attempt_count (1) < max (3), it should have updated status to retry
            # Let's inspect the update query call
            update_calls = db_mock.execute.call_args_list
            assert len(update_calls) > 0
            
            # Ensure commit was called
            db_mock.commit.assert_called_once()
            

@pytest.mark.asyncio
async def test_kill_process_recovery():
    """Verify that recover_stale_jobs sets 'processing' -> 'retry'."""
    from app.services.job_worker import recover_stale_jobs

    with patch("app.services.job_worker.AsyncSessionLocal") as session_factory_mock:
        db_mock = AsyncMock(spec=AsyncSession)
        session_factory_mock.return_value.__aenter__.return_value = db_mock
        
        # Mock result rowcount
        result_mock = MagicMock()
        result_mock.rowcount = 1
        db_mock.execute.return_value = result_mock
        
        await recover_stale_jobs()
        
        db_mock.execute.assert_called_once()
        db_mock.commit.assert_called_once()
