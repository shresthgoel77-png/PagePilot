import asyncio
import io
import json
import logging
from unittest.mock import patch, MagicMock, AsyncMock

import os
os.environ["CLERK_SECRET_KEY"] = "test_key"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://user:pass@localhost:5432/db"
os.environ["QDRANT_URL"] = "http://localhost:6333"
os.environ["SECRET_KEY"] = "test_secret"
os.environ["UPLOAD_DIR"] = "./uploads"
os.environ["GEMINI_API_KEY"] = "test_gemini"

from fastapi.testclient import TestClient
from app.main import app, logger
from app.core.metrics import (
    gemini_requests_total,
    qdrant_requests_total,
    reranker_requests_total,
    ingestion_jobs_total,
)
from app.core.logging_setup import correlation_id_var
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
logging.getLogger("researchos").addHandler(stream_handler)

def reset_metrics():
    gemini_requests_total._metrics.clear()
    qdrant_requests_total._metrics.clear()
    reranker_requests_total._metrics.clear()
    ingestion_jobs_total._metrics.clear()
    log_stream.seek(0)
    log_stream.truncate(0)

# Instantiate client explicitly with lifespan disabled
with TestClient(app, raise_server_exceptions=False) as client:
    
    async def run_tests():
        results = []
        
        # Test 1: Qdrant unreachable
        reset_metrics()
        # Mock Context of HTTP request providing correlation ID bounds 
        request_id = str(uuid.uuid4())
        correlation_id_var.set(request_id)
        
        with patch('app.services.vector_store.VectorStoreService.search', side_effect=ConnectionRefusedError("Connection refused by Qdrant")):
            with patch('app.services.embeddings.EmbeddingService.generate_embeddings', return_value=[[0.1]*768]):
                svc = RetrievalService()
                try:
                    svc.retrieve(project_id="test_pid", query="test_query")
                except ConnectionRefusedError:
                    pass
        
        qdrant_logs = [line for line in log_stream.getvalue().splitlines() if line.strip()]
        results.append("=== 1. Qdrant Unreachable ===")
        results.append("Logs:")
        for log in qdrant_logs: results.append("  " + log)
        resp = client.get("/metrics")
        for line in resp.text.splitlines():
            if 'qdrant_requests_total' in line: results.append("  Metric: " + line)


        # Test 2: Reranker Fallback
        reset_metrics()
        correlation_id_var.set(request_id)
        
        class DummyResult:
            def __init__(self):
                self.payload = MagicMock()
                self.payload.text = "dummy text"
                self.score = 0.0

        with patch('app.services.vector_store.VectorStoreService.search', return_value=[DummyResult()]):
            with patch('app.services.embeddings.EmbeddingService.generate_embeddings', return_value=[[0.1]*768]):
                with patch('app.services.retrieval.cross_encoder_model', MagicMock()) as mock_encoder:
                    import app.services.retrieval
                    app.services.retrieval.RERANKER_AVAILABLE = True
                    mock_encoder.predict.side_effect = Exception("Model out of memory")
                    
                    svc = RetrievalService()
                    # Won't throw because it's a fallback mechanism explicitly mapped inside retrieval.py
                    svc.retrieve(project_id="test_pid", query="test_query")
                    
        reranker_logs = [line for line in log_stream.getvalue().splitlines() if line.strip()]
        results.append("\n=== 2. Reranker Fallback ===")
        results.append("Logs:")
        for log in reranker_logs: results.append("  " + log)
        resp = client.get("/metrics")
        for line in resp.text.splitlines():
            if 'reranker_requests_total' in line: results.append("  Metric: " + line)
            
            
        # Test 3: Gemini Timeout 
        reset_metrics()
        correlation_id_var.set(request_id)
        
        import app.services.chat_engine
        try:
            with patch.object(app.services.chat_engine.genai.Client, 'models') as mock_models:
                mock_models.generate_content.side_effect = Exception("Deadline exceeded fetching Gemini")
                engine = ChatEngine(chat_service=MagicMock())
                await engine._classify_query("test classification")
        except: pass
        
        gemini_logs = [line for line in log_stream.getvalue().splitlines() if line.strip()]
        results.append("\n=== 3. Gemini Timeout ===")
        results.append("Logs:")
        for log in gemini_logs: results.append("  " + log)
        resp = client.get("/metrics")
        for line in resp.text.splitlines():
            if 'gemini_requests_total' in line: results.append("  Metric: " + line)


        # Test 4: Ingestion Pipeline Error
        reset_metrics()
        
        with patch('app.services.indexing_pipeline.AsyncSessionLocal') as mock_db:
            mock_db_instance = MagicMock()
            mock_pdf = MagicMock(id=uuid.uuid4(), file_path="crash.pdf", project_id=str(uuid.uuid4()))
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_pdf
            mock_db_instance.execute = AsyncMock(return_value=mock_result)
            mock_db_instance.commit = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_db_instance
            
            with patch('app.services.pdf_parser.PDFParserService.parse_pdf_generator', side_effect=ValueError("PDF corrupted structurally entirely")):
                try:
                    await run_indexing(project_id=str(mock_pdf.project_id), file_path="crash.pdf", user_id="test")
                except ValueError:
                    pass
        
        ingestion_logs = [line for line in log_stream.getvalue().splitlines() if line.strip()]
        results.append("\n=== 4. Ingestion Failure ===")
        results.append("Logs:")
        for log in ingestion_logs: results.append("  " + log)
        resp = client.get("/metrics")
        for line in resp.text.splitlines():
            if 'ingestion_jobs_total' in line: results.append("  Metric: " + line)


        # Output complete validation payload explicitly 
        with open("verify_output_2.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(results))
        print("Execution tracking explicitly dumped to verify_output_2.txt")

    asyncio.run(run_tests())
