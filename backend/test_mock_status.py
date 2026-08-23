"""Mock test suite to verify pipeline status transitions without Docker."""
import asyncio
import uuid
import pytest
import os
from datetime import datetime, timezone
from unittest.mock import MagicMock, AsyncMock, patch

# Mock env vars
os.environ["CLERK_SECRET_KEY"] = "mock"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://mock:pass@localhost/mock"
os.environ["QDRANT_URL"] = "http://localhost:6333"

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.pdf import PDF, PDFStatus
from app.services.indexing_pipeline import run as run_pipeline

@pytest.mark.asyncio
async def test_pipeline_status_transitions():
    project_id = uuid.uuid4()
    file_path = "/mock/path.pdf"
    user_id = uuid.uuid4()

    mock_pdf = PDF(
        id=uuid.uuid4(),
        project_id=project_id,
        file_path=file_path,
        filename="test.pdf",
        status=PDFStatus.queued,
        progress=0
    )

    db_mock = AsyncMock(spec=AsyncSession)
    res_mock = MagicMock()
    res_mock.scalar_one_or_none.return_value = mock_pdf
    db_mock.execute.return_value = res_mock

    # Track status/progress pairs as they are committed
    transitions = []
    
    # Store changes when commit is called
    async def track_commit():
        transitions.append((mock_pdf.status, mock_pdf.progress))
        
    db_mock.commit.side_effect = track_commit

    with patch("app.services.indexing_pipeline.AsyncSessionLocal") as session_factory:
        session_factory.return_value.__aenter__.return_value = db_mock
        
        with patch("app.services.pdf_parser.PDFParserService.parse_pdf_generator") as parse_mock:
            parse_mock.return_value = [({"page": 1, "is_ocr": True}, [{"text": "mock", "project_id": str(project_id), "pdf_id": str(mock_pdf.id), "page_number": 1, "chunk_index": 0, "filename": "test.pdf"}])]
            
            with patch("app.services.embeddings.EmbeddingService.generate_embeddings") as gen_embed_mock, \
                 patch("app.services.vector_store.VectorStoreService.upsert_chunks") as upsert_mock:
                gen_embed_mock.return_value = [[0.0]*768]
                upsert_mock.return_value = None
                
                await run_pipeline(project_id, file_path, user_id)
                
    # Verify the transitions recorded correctly
    assert transitions == [
        (PDFStatus.parsing, 10),
        (PDFStatus.ocr, 25),
        (PDFStatus.embedding, 50),
        (PDFStatus.indexing, 75),
        (PDFStatus.ready, 100),
    ]
    # Check indexed_at got set natively
    assert mock_pdf.indexed_at is not None
