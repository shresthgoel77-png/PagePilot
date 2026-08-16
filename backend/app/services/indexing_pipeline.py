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
        await db.commit()

        # Parse and embed — let exceptions propagate for worker retry logic
        parser = PDFParserService()
        embeddings = EmbeddingService()

        chunks = parser.parse_pdf(
            pdf_id=str(pdf.id),
            project_id=str(pdf.project_id),
            filename=pdf.filename,
            file_path=pdf.file_path,
        )

        full_text = "\n".join([c["text"] for c in chunks])
        pdf.parsed_text = full_text

        embeddings.index_pdf_chunks(str(pdf.id), chunks)

        pdf.status = PDFStatus.parsed
        await db.commit()
        logger.info(f"Indexing pipeline completed for pdf {pdf.id}")
