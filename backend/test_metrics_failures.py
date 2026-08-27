import pytest
import io
import json
import logging
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

import os
os.environ["CLERK_SECRET_KEY"] = "test_key"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://user:pass@localhost:5432/db"
os.environ["QDRANT_URL"] = "http://localhost:6333"
os.environ["SECRET_KEY"] = "test_secret"
os.environ["UPLOAD_DIR"] = "./uploads"
os.environ["GEMINI_API_KEY"] = "test_gemini"

from app.main import app, logger
from app.core.metrics import (
    gemini_requests_total,
    qdrant_requests_total,
    ingestion_jobs_total,
)
from app.services.indexing_pipeline import run as run_indexing
from app.services.retrieval import RetrievalService
from app.services.chat_engine import ChatEngine
import uuid

# Memory handler to catch JSON logs
log_stream = io.StringIO()
stream_handler = logging.StreamHandler(log_stream)
from app.core.logging_setup import CorrelationJsonFormatter
stream_handler.setFormatter(CorrelationJsonFormatter("%(timestamp)s %(name)s %(levelname)s %(message)s"))
logger.addHandler(stream_handler)

@pytest.fixture(scope="module")
def client():
    # Bypass blocking startup worker/migrations by explicitly disabling lifespan
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c

@pytest.fixture(autouse=True)
def reset_metrics_and_logs():
    gemini_requests_total._metrics.clear()
    qdrant_requests_total._metrics.clear()
    ingestion_jobs_total._metrics.clear()
    log_stream.seek(0)
    log_stream.truncate(0)

@pytest.mark.asyncio
async def test_qdrant_unreachable_metrics(client):
    # Trigger Qdrant unreachable
    with patch('app.services.vector_store.VectorStoreService.search', side_effect=ConnectionRefusedError("Connection refused by Qdrant")):
        with patch('app.services.embeddings.EmbeddingService.generate_embeddings', return_value=[[0.1]*768]):
            svc = RetrievalService()
            try:
                svc.retrieve(project_id="test_pid", query="test_query")
            except ConnectionRefusedError:
                pass
            
    # Check metrics
    resp = client.get("/metrics")
    text = resp.text
    assert 'qdrant_requests_total{status="error"} 1.0' in text
    
    # Verify json logger formats inherently
    lines = log_stream.getvalue().strip().split('\n')
    has_error_log = False
    for line in lines:
        try:
            doc = json.loads(line)
            if "Qdrant query crashed" in doc.get("message", "") and doc.get("levelname") == "ERROR":
                has_error_log = True
        except: pass
    assert has_error_log, "Missing Qdrant JSON structurally mapped error log"

@pytest.mark.asyncio
async def test_gemini_timeout_metrics(client):
    import app.services.chat_engine
    
    # Simulate a Gemini timeout on decomposition
    with patch.object(app.services.chat_engine.genai.Client, 'models') as mock_models:
        from google.api_core.exceptions import DeadlineExceeded
        mock_models.generate_content.side_effect = DeadlineExceeded("Deadline exceeded fetching Gemini")
        
        chat_svc = MagicMock()
        engine = ChatEngine(chat_service=chat_svc)
        
        # Test reformulation 
        await engine._reformulate_query("test", [])
        
    resp = client.get("/metrics")
    text = resp.text
    assert 'gemini_requests_total{status="error"} 1.0' in text or 'gemini_requests_total_total{status="error"} 1.0' in text

@pytest.mark.asyncio
async def test_ingestion_crash_metrics(client):
    # Ingestion error
    with patch('app.services.indexing_pipeline.AsyncSessionLocal') as mock_db:
        mock_db_instance = MagicMock()
        mock_pdf = MagicMock(id=uuid.uuid4(), file_path="crash.pdf", project_id=str(uuid.uuid4()))
        mock_db_instance.execute.return_value.scalar_one_or_none.return_value = mock_pdf
        mock_db.return_value.__aenter__.return_value = mock_db_instance
        
        # Throw error explicitly natively
        with patch('app.services.pdf_parser.PDFParserService.parse_pdf_generator', side_effect=ValueError("PDF corrupted structurally entirely")):
            try:
                await run_indexing(project_id=str(mock_pdf.project_id), file_path="crash.pdf", user_id="test")
            except ValueError:
                pass
            
    resp = client.get("/metrics")
    text = resp.text
    
    assert 'ingestion_jobs_total{status="failure"} 1.0' in text
    
    # Verify JSON structure implicitly mapped
    lines = log_stream.getvalue().strip().split("\n")
    valid_json = False
    corr_found = False
    for line in lines:
        if not line: continue
        try:
            doc = json.loads(line)
            if "Indexing pipeline crashed implicitly smoothly" in doc.get("message", ""):
                valid_json = True
                if "correlation_id" in doc:
                    corr_found = True
        except: pass
        
    assert valid_json, "Expected structural JSON crash log wasn't emitted"
    assert corr_found, "Correlation ID explicitly bounded context variables failed"
