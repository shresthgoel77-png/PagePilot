import os
import sys
import io
import uuid
import pytest
from unittest.mock import MagicMock, AsyncMock
from unittest import mock
from reportlab.pdfgen import canvas
import asyncio
from datetime import datetime, timezone

# Inject globally to bypass missing underlying EasyOCR pip module locally
sys.modules['easyocr'] = MagicMock()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient

# Setup environment before importing app
os.environ["CLERK_SECRET_KEY"] = "sk_test_dummy"
os.environ["GEMINI_API_KEY"] = "mock_gemini_api_key_for_testing"

from app.main import app
from app.db.session import get_db, AsyncSessionLocal
from app.models.project import Project
from app.models.user import User
from app.models.pdf import PDF, PDFStatus
from app.models.ingestion_job import IngestionJob, JobStatus
import app.services.job_worker as worker
from app.services import ocr_service
from app.services import vector_store
from app.services import embeddings
from datetime import datetime, timezone

# Mock the database explicitly for API calls
mock_db = AsyncMock()

async def mock_refresh(obj):
    if not getattr(obj, "id", None):
        obj.id = uuid.uuid4()
    if not getattr(obj, "created_at", None):
        obj.created_at = datetime.now(timezone.utc)
    if not getattr(obj, "updated_at", None):
        obj.updated_at = datetime.now(timezone.utc)

# Setup default retrieve matching to prevent duplicate triggers
def setup_mock_db():
    res_mock = MagicMock()
    res_mock.scalar_one_or_none.return_value = PDF(id=uuid.uuid4(), project_id=uuid.uuid4(), file_path="dummy", filename="dummy", original_name="dummy", file_hash="dummy", status=PDFStatus.uploaded, created_at=datetime.now(timezone.utc))
    res_mock.scalars.return_value.all.return_value = []
    mock_db.execute = AsyncMock(return_value=res_mock)
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock(side_effect=mock_refresh)
    mock_db.add = MagicMock() # Sync
    return mock_db

# Initialize mock_db securely immediately for global tests correctly optimally
setup_mock_db()

async def override_get_db():
    yield setup_mock_db()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="session")
def dummy_pdfs(tmp_path_factory):
    d = tmp_path_factory.mktemp("dummy_pdfs")
    result = {}
    
    # 1. normal.pdf
    norm_path = d / "normal.pdf"
    c = canvas.Canvas(str(norm_path))
    c.drawString(100, 100, "This is a normal PDF document with text payload.")
    c.save()
    result["normal"] = norm_path
    
    # 2. scanned.pdf
    lazy_path = d / "scanned.pdf"
    c = canvas.Canvas(str(lazy_path))
    c.showPage()
    c.save()
    result["scanned"] = lazy_path
    
    # 3. large.pdf (100 pages)
    large_path = d / "large.pdf"
    c = canvas.Canvas(str(large_path))
    for i in range(101):
        c.drawString(100, 100, f"Page number {i} with a large amount of text.")
        c.showPage()
    c.save()
    result["large"] = large_path
    
    # 4. corrupt.pdf (literal junk)
    corrupt_path = d / "corrupt.pdf"
    with open(corrupt_path, "wb") as f:
        f.write(b"not a valid pdf structural binary format")
    result["corrupt"] = corrupt_path
    
    return result

class MockTokenPayload:
    def __init__(self, is_signed_in=True, sub="user_123", email="user1@example.com"):
        self.is_signed_in = is_signed_in
        self.payload = {"sub": sub, "email": email}

@pytest.fixture
def mock_clerk():
    with mock.patch("app.core.clerk_auth.clerk_client.authenticate_request") as mock_auth:
        yield mock_auth

def test_auth_missing_token():
    response = client.post("/projects", json={"name": "Test Missing Auth", "description": "None"})
    assert response.status_code == 401
    assert "Could not validate credentials" in response.json().get("detail", "")

def test_auth_invalid_token(mock_clerk):
    mock_clerk.return_value = MockTokenPayload(is_signed_in=False)
    response = client.post("/projects", json={"name": "Test Invalid", "description": "None"}, headers={"Authorization": "Bearer EXPIRED_TOKEN"})
    assert response.status_code == 401

def test_auth_valid_token(mock_clerk):
    # Mock project resolution dynamically if needed cleanly
    mock_clerk.return_value = MockTokenPayload(is_signed_in=True, sub="valid_user", email="valid@example.com")
    
    response = client.post("/projects", json={"name": "Valid Project", "description": "Valid Content"}, headers={"Authorization": "Bearer GOOD_TOKEN"})
    assert response.status_code == 201

def test_auth_cross_user_isolation(mock_clerk):
    mock_clerk.return_value = MockTokenPayload(is_signed_in=True, sub="user_2", email="u2@example.com")
    
    with mock.patch("app.routers.pdfs.verify_project") as mock_vp:
        # Cross user raises HTTP 404
        from fastapi import HTTPException
        mock_vp.side_effect = HTTPException(status_code=404, detail="Ownership bounds unresolvable intrinsically tracking projects")
        
        files = {"file": ("dummy.pdf", b"dummy content", "application/pdf")}
        upload_resp = client.post(f"/projects/{uuid.uuid4()}/pdfs", headers={"Authorization": "Bearer TOKEN2"}, files=files)
        
        assert upload_resp.status_code == 404

@pytest.mark.asyncio
async def test_normal_ingestion(dummy_pdfs, mock_clerk):
    job = IngestionJob(id=uuid.uuid4(), pdf_id=uuid.uuid4(), file_path=dummy_pdfs["normal"], project_id=uuid.uuid4(), user_id=uuid.uuid4(), attempt_count=0, max_attempts=3, status=JobStatus.processing)

    with mock.patch("app.services.job_worker.AsyncSessionLocal") as sf_mock, mock.patch("app.services.indexing_pipeline.AsyncSessionLocal", create=True) as sf_mock2:
        sf_mock.return_value.__aenter__.return_value = mock_db
        sf_mock2.return_value.__aenter__.return_value = mock_db
        with mock.patch("app.services.vector_store.VectorStoreService.upsert_chunks") as mock_upsert:
            with mock.patch("app.services.embeddings.genai.Client") as mock_genai:
                mock_upsert.return_value = None
                class Emb: values = [0.1] * 768
                class DummyResp: embeddings = [Emb()]
                mock_genai.return_value.models.embed_content.return_value = DummyResp()
                
                mock_db.execute.return_value.scalar_one_or_none.return_value.file_path = job.file_path
                await worker.process_job(job)
                calls = mock_db.execute.call_args_list
                params = [c.args[0].compile().params for c in calls if hasattr(c.args[0], "compile")]
                assert any(p.get("status") == JobStatus.completed for p in params)

@pytest.mark.asyncio
async def test_large_pdf_ingestion(dummy_pdfs, mock_clerk):
    job = IngestionJob(id=uuid.uuid4(), pdf_id=uuid.uuid4(), file_path=dummy_pdfs["large"], project_id=uuid.uuid4(), user_id=uuid.uuid4(), attempt_count=0, max_attempts=3, status=JobStatus.processing)

    with mock.patch("app.services.job_worker.AsyncSessionLocal") as sf_mock, mock.patch("app.services.indexing_pipeline.AsyncSessionLocal", create=True) as sf_mock2:
        sf_mock.return_value.__aenter__.return_value = mock_db
        sf_mock2.return_value.__aenter__.return_value = mock_db
        with mock.patch("app.services.vector_store.VectorStoreService.upsert_chunks") as mock_upsert:
            with mock.patch("app.services.embeddings.genai.Client") as mock_genai:
                mock_upsert.return_value = None
                class Emb: values = [0.1] * 768
                class DummyResp: embeddings = [Emb()]
                mock_genai.return_value.models.embed_content.return_value = DummyResp()
                
                mock_db.execute.return_value.scalar_one_or_none.return_value.file_path = job.file_path
                await worker.process_job(job)
                calls = mock_db.execute.call_args_list
                params = [c.args[0].compile().params for c in calls if hasattr(c.args[0], "compile")]
                assert any(p.get("status") == JobStatus.completed for p in params)

@pytest.mark.asyncio
async def test_corrupt_pdf(dummy_pdfs, mock_clerk):
    job = IngestionJob(id=uuid.uuid4(), pdf_id=uuid.uuid4(), file_path=dummy_pdfs["corrupt"], project_id=uuid.uuid4(), user_id=uuid.uuid4(), attempt_count=0, max_attempts=3, status=JobStatus.processing)

    with mock.patch("app.services.job_worker.AsyncSessionLocal") as sf_mock, mock.patch("app.services.indexing_pipeline.AsyncSessionLocal", create=True) as sf_mock2:
        sf_mock.return_value.__aenter__.return_value = mock_db
        sf_mock2.return_value.__aenter__.return_value = mock_db
        
        mock_db.execute.return_value.scalar_one_or_none.return_value.file_path = job.file_path
        await worker.process_job(job)

        calls = mock_db.execute.call_args_list
        params = [c.args[0].compile().params for c in calls if hasattr(c.args[0], "compile")]
        assert any(p.get("status") in (JobStatus.failed, JobStatus.retry) for p in params)

@pytest.mark.asyncio
async def test_embedding_failure_zero_vectors(dummy_pdfs):
    job = IngestionJob(id=uuid.uuid4(), pdf_id=uuid.uuid4(), file_path=dummy_pdfs["normal"], project_id=uuid.uuid4(), user_id=uuid.uuid4(), attempt_count=3, max_attempts=3, status=JobStatus.processing)

    with mock.patch("app.services.job_worker.AsyncSessionLocal") as sf_mock, mock.patch("app.services.indexing_pipeline.AsyncSessionLocal", create=True) as sf_mock2:
        sf_mock.return_value.__aenter__.return_value = mock_db
        sf_mock2.return_value.__aenter__.return_value = mock_db
        with mock.patch("app.services.embeddings.EmbeddingService.generate_embeddings") as mock_embed:
            mock_embed.side_effect = Exception("Simulated Embedding Dropout - Zero Vectors Permitted: FALSE")
            mock_db.execute.return_value.scalar_one_or_none.return_value.file_path = job.file_path
            await worker.process_job(job)
            
        calls = mock_db.execute.call_args_list
        params = [c.args[0].compile().params for c in calls if hasattr(c.args[0], "compile")]
        print(f"FAILED PARAMS: {params}")
        assert any(p.get("status") in (JobStatus.failed, "failed", "JobStatus.failed", JobStatus.retry) for p in params)
        assert any("Embedding Dropout" in str(v) for p in params for v in p.values())

@pytest.mark.asyncio
async def test_ocr_and_qdrant_failure(dummy_pdfs):
    job = IngestionJob(id=uuid.uuid4(), pdf_id=uuid.uuid4(), file_path=dummy_pdfs["scanned"], project_id=uuid.uuid4(), user_id=uuid.uuid4(), attempt_count=0, max_attempts=3, status=JobStatus.processing)

    with mock.patch("app.services.job_worker.AsyncSessionLocal") as sf_mock, mock.patch("app.services.indexing_pipeline.AsyncSessionLocal", create=True) as sf_mock2:
        sf_mock.return_value.__aenter__.return_value = mock_db
        sf_mock2.return_value.__aenter__.return_value = mock_db
        
        with mock.patch("app.services.ocr_service.OCRService.extract_text") as mock_ocr:
            with mock.patch("app.services.embeddings.genai.Client") as mock_genai:
                with mock.patch("app.services.vector_store.VectorStoreService.upsert_chunks") as mock_upsert:
                    mock_ocr.return_value = "Recovered text natively representing OCR."
                    class Emb: values = [0.1] * 768
                    class DummyResp: embeddings = [Emb()]
                    mock_genai.return_value.models.embed_content.return_value = DummyResp()
                    
                    mock_upsert.side_effect = Exception("Simulated Qdrant Timeout")
                    mock_db.execute.return_value.scalar_one_or_none.return_value.file_path = job.file_path
                    await worker.process_job(job)
                    
        calls = mock_db.execute.call_args_list
        params = [c.args[0].compile().params for c in calls if hasattr(c.args[0], "compile")]
        assert any(p.get("status") == JobStatus.retry for p in params)
        assert any("Qdrant Timeout" in str(v) for p in params for v in p.values())

@pytest.mark.asyncio
async def test_simulated_ocr_failure(dummy_pdfs):
    job = IngestionJob(id=uuid.uuid4(), pdf_id=uuid.uuid4(), file_path=dummy_pdfs["scanned"], project_id=uuid.uuid4(), user_id=uuid.uuid4(), attempt_count=0, max_attempts=3, status=JobStatus.processing)

    with mock.patch("app.services.job_worker.AsyncSessionLocal") as sf_mock, mock.patch("app.services.indexing_pipeline.AsyncSessionLocal", create=True) as sf_mock2:
        sf_mock.return_value.__aenter__.return_value = mock_db
        sf_mock2.return_value.__aenter__.return_value = mock_db
        
        with mock.patch("app.services.ocr_service.OCRService.extract_text") as mock_ocr:
            mock_ocr.side_effect = Exception("Simulated OCR Dropout")
            
            mock_db.execute.return_value.scalar_one_or_none.return_value.file_path = job.file_path
            await worker.process_job(job)
            
        calls = mock_db.execute.call_args_list
        params = [c.args[0].compile().params for c in calls if hasattr(c.args[0], "compile")]
        # Assert failure or retry based on what process_job does to job status. If transient it's retry.
        assert any(p.get("status") in (JobStatus.retry, JobStatus.failed) for p in params)
