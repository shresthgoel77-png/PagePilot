import asyncio
import uuid
import sys
import os
from unittest import mock

sys.path.append(os.getcwd())

from app.models.ingestion_job import IngestionJob, JobStatus
from app.models.pdf import PDF, PDFStatus
from app.services import job_worker as worker

async def run():
    db = mock.AsyncMock()
    # mimic dummy_pdfs["normal"] file path, assuming normal.pdf exists since pytest creates it but here we just make a new one!
    from reportlab.pdfgen import canvas
    c = canvas.Canvas("test_dump.pdf")
    c.drawString(100, 100, "Simulated valid payload extracted natively.")
    c.save()

    job = IngestionJob(id=uuid.uuid4(), pdf_id=uuid.uuid4(), file_path="test_dump.pdf", project_id=uuid.uuid4(), user_id=uuid.uuid4(), attempt_count=3, max_attempts=3, status=JobStatus.processing)

    db.execute.return_value.scalar_one_or_none.return_value = PDF(id=uuid.uuid4(), project_id=uuid.uuid4(), file_path="test_dump.pdf", filename="test_dump.pdf", original_name="test_dump.pdf", file_hash="test", status=PDFStatus.uploaded)

    with mock.patch("app.services.job_worker.AsyncSessionLocal") as f, mock.patch("app.services.indexing_pipeline.AsyncSessionLocal", create=True) as f2, mock.patch("app.services.embeddings.genai.Client") as m_g:
        f.return_value.__aenter__.return_value = db
        f2.return_value.__aenter__.return_value = db
        m_g.return_value.models.embed_content.side_effect = Exception("test")
        
        await worker.process_job(job)
        
        calls = db.execute.call_args_list
        params = [c.args[0].compile().params for c in calls if hasattr(c.args[0], "compile")]
        for p in params:
            print("PARAM LIST ELEMENT:", p)

asyncio.run(run())
