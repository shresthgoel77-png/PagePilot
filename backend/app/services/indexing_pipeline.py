import logging
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.pdf import PDF, PDFStatus
from app.services.pdf_parser import PDFParserService
from app.services.embeddings import EmbeddingService

logger = logging.getLogger("researchos.indexing_pipeline")


async def run(project_id, file_path, user_id):
    """Execute the PDF parsing and vector-indexing pipeline.

    Called by the job worker. Exceptions propagate upward so the worker
    can handle retry / failure bookkeeping.
    """
    logger.info(f"Indexing pipeline starting for artifact: {file_path}")

    async with AsyncSessionLocal() as db:
        stmt = select(PDF).where(PDF.file_path == file_path, PDF.project_id == project_id)
        result = await db.execute(stmt)
        pdf = result.scalar_one_or_none()

        if not pdf:
            raise ValueError(f"PDF record not found for file_path={file_path}, project_id={project_id}")

        pdf.status = PDFStatus.parsing
        pdf.progress = 10
        await db.commit()

        # Parse and embed — run blocking tasks off the main event loop
        import asyncio
        parser = PDFParserService()
        embeddings = EmbeddingService()

        # Execute CPU-bound parsing in a separate thread
        extracted_pages, chunks = await asyncio.to_thread(
            parser.parse_pdf,
            str(pdf.id),
            str(pdf.project_id),
            pdf.filename,
            pdf.file_path,
        )

        # Store explicit structural mappings securely globally avoiding flattened blob destruction 
        pdf.parsed_text = extracted_pages

        # Store explicit structural mappings securely globally avoiding flattened blob destruction 
        pdf.parsed_text = extracted_pages

        # Validate extraction constraints: 
        # If absolute absence of text or 100% of pages natively failed resolution
        total_valid = sum(1 for p in extracted_pages if not p.get("needs_ocr", False))
        if total_valid == 0:
            pdf.status = PDFStatus.error
            pdf.progress = 30
            pdf.error_message = "Extraction bounds yielded zero native geometries implicitly terminating dynamically safely."
            await db.commit()
            raise ValueError("Zero valid components safely mapped structurally explicitly terminating limits.")

        pdf.status = PDFStatus.embedding
        pdf.progress = 50
        await db.commit()

        pdf.status = PDFStatus.indexing
        pdf.progress = 75
        await db.commit()

        # Execute I/O-bound vector indexing in a separate thread
        await asyncio.to_thread(
            embeddings.index_pdf_chunks,
            str(pdf.id),
            chunks
        )

        pdf.status = PDFStatus.ready
        pdf.progress = 100
        from datetime import datetime, timezone
        pdf.indexed_at = datetime.now(timezone.utc)
        await db.commit()
        logger.info(f"Indexing pipeline completed for pdf {pdf.id}")
