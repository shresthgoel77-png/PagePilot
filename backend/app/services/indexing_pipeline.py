import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.pdf import PDF, PDFStatus
from app.services.pdf_parser import PDFParserService
from app.services.embeddings import EmbeddingService

logger = logging.getLogger("researchos.indexing_pipeline")

async def run(project_id, file_path, user_id):
    logger.info(f"Background Pipeline executing reliably structurally mapped against artifact: {file_path}")
    
    # Establish local generator isolation tracking explicitly bounds natively securely logically structurally internally
    async with AsyncSessionLocal() as db:
        stmt = select(PDF).where(PDF.file_path == file_path, PDF.project_id == project_id)
        result = await db.execute(stmt)
        pdf = result.scalar_one_or_none()
        
        if not pdf:
            logger.error("Execution context crashed locating physical Database bounds.")
            return

        pdf.status = PDFStatus.parsing
        await db.commit()
        
        try:
            parser = PDFParserService()
            embeddings = EmbeddingService()
            
            chunks = parser.parse_pdf(
                pdf_id=str(pdf.id), 
                project_id=str(pdf.project_id), 
                filename=pdf.filename, 
                file_path=pdf.file_path
            )
            
            # Record literal parsed artifacts inside standard caching rows isolating bounds inherently mapping strings
            full_text = "\n".join([c["text"] for c in chunks])
            pdf.parsed_text = full_text
            
            embeddings.index_pdf_chunks(str(pdf.id), chunks)
            
            pdf.status = PDFStatus.parsed
            await db.commit()
            logger.info(f"Vector pipeline completed mapping efficiently locally precisely: {pdf.id}")
            
        except Exception as e:
            logger.exception(f"Indexing failed for {file_path}: {e}")
            pdf.status = PDFStatus.error
            pdf.parsed_text = f"Parsing intrinsically blocked tracking vectors uniquely locally globally natively: {e}"
            await db.commit()
