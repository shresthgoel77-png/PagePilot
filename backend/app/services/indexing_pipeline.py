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

        import asyncio, json, os, uuid
        from app.core.config import settings
        
        parser = PDFParserService()
        embeddings = EmbeddingService()
        
        temp_chunks_path = os.path.join(settings.UPLOAD_DIR, f"chunks_{pdf.id}.jsonl")
        temp_vectors_path = os.path.join(settings.UPLOAD_DIR, f"vectors_{pdf.id}.jsonl")
        
        def do_parsing():
            t_pages = 0
            t_valid = 0
            has_ocr = False
            gen = parser.parse_pdf_generator(str(pdf.id), str(pdf.project_id), pdf.filename, pdf.file_path)
            with open(temp_chunks_path, "w") as f:
                for page_data, page_chunks in gen:
                    t_pages += 1
                    if page_data.get("needs_ocr", False) or page_data.get("is_ocr", False):
                        has_ocr = True
                    else:
                        t_valid += 1
                    for chunk in page_chunks:
                        f.write(json.dumps(chunk) + "\n")
            return t_valid, t_pages, has_ocr
            
        t_valid, t_pages, has_ocr = await asyncio.to_thread(do_parsing)
        
        if has_ocr:
            pdf.status = PDFStatus.ocr
            pdf.progress = 25
            await db.commit()
            
        if t_pages == 0:
            logger.warning(f"Warning: Absolute absence of valid OCR structures found inside PDF target '{file_path}'.")
            
        if t_valid == 0 and t_pages > 0 and not has_ocr:
            pdf.status = PDFStatus.error
            pdf.error_message = "Valid components completely failed extraction limit constraints globally"
            await db.commit()
            raise ValueError("Zero valid components safely mapped structurally explicitly terminating limits.")
            
        pdf.status = PDFStatus.embedding
        pdf.progress = 50
        await db.commit()
        
        def do_embedding():
            if not os.path.exists(temp_chunks_path): return
            
            accum_chunks = []
            with open(temp_chunks_path, "r") as f_in, open(temp_vectors_path, "w") as f_out:
                for line in f_in:
                    accum_chunks.append(json.loads(line))
                    if len(accum_chunks) >= embeddings.batch_size:
                        t_batch = [c["text"] for c in accum_chunks]
                        vecs = embeddings.generate_embeddings(t_batch)
                        for c, v in zip(accum_chunks, vecs):
                            f_out.write(json.dumps({"payload": c, "vector": v}) + "\n")
                        accum_chunks.clear()
                if accum_chunks:
                    t_batch = [c["text"] for c in accum_chunks]
                    vecs = embeddings.generate_embeddings(t_batch)
                    for c, v in zip(accum_chunks, vecs):
                        f_out.write(json.dumps({"payload": c, "vector": v}) + "\n")

        await asyncio.to_thread(do_embedding)
        
        pdf.status = PDFStatus.indexing
        pdf.progress = 75
        await db.commit()
        
        def do_indexing():
            if not os.path.exists(temp_vectors_path): return
            batch = []
            with open(temp_vectors_path, "r") as f_in:
                for line in f_in:
                    batch.append(json.loads(line))
                    if len(batch) >= embeddings.batch_size:
                        embeddings.vector_store.upsert_chunks(batch)
                        batch.clear()
                if batch:
                    embeddings.vector_store.upsert_chunks(batch)
                    
        await asyncio.to_thread(do_indexing)
        
        if os.path.exists(temp_chunks_path): os.remove(temp_chunks_path)
        if os.path.exists(temp_vectors_path): os.remove(temp_vectors_path)

        pdf.status = PDFStatus.ready
        pdf.progress = 100
        from datetime import datetime, timezone
        pdf.indexed_at = datetime.now(timezone.utc)
        await db.commit()
        logger.info(f"Indexing pipeline completed strictly sequentially for pdf {pdf.id}")

