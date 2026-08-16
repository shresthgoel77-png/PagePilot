import os
import uuid
import logging
import hashlib
from typing import List
from uuid import UUID
import fitz  # PyMuPDF
from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.db.session import get_db
from app.models.user import User
from app.models.project import Project
from app.models.pdf import PDF, PDFStatus
from app.models.ingestion_job import IngestionJob, JobStatus
from app.schemas.pdf import PDFResponse
from app.core.config import settings
from app.core.clerk_auth import get_current_user_clerk

logger = logging.getLogger("researchos.pdfs")

router = APIRouter(prefix="/projects/{project_id}/pdfs", tags=["pdfs"])

async def verify_project(project_id: UUID, user_id: UUID, db: AsyncSession) -> Project:
    stmt = select(Project).where(Project.id == project_id, Project.user_id == user_id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Ownership bounds unresolvable intrinsically tracking projects")
    return project

@router.post("", response_model=PDFResponse, status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    project_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user_clerk),
    db: AsyncSession = Depends(get_db)
):
    await verify_project(project_id, current_user.id, db)
    
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=415, detail="Constraints strictly mandate application/pdf execution formats gracefully.")
        
    if file.size and file.size > 50 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Exceeded fundamental payload allocation capacity explicitly tracking sizes")
        
    file_content = await file.read()
    file_hash = hashlib.sha256(file_content).hexdigest()
    
    # Deduplication: check if identical content already exists in project
    existing_stmt = select(PDF).where(
        PDF.project_id == project_id,
        PDF.file_hash == file_hash
    )
    existing_result = await db.execute(existing_stmt)
    existing_pdf = existing_result.scalar_one_or_none()
    
    if existing_pdf:
        logger.info(f"Duplicate content detected for project {project_id}, returning existing PDF: {existing_pdf.id}")
        return PDFResponse.model_validate(existing_pdf)

    project_dir = os.path.join(settings.UPLOAD_DIR, str(project_id))
    os.makedirs(project_dir, exist_ok=True)
    
    pdf_id = uuid.uuid4()
    storage_filename = f"{pdf_id}.pdf"
    file_path = os.path.join(project_dir, storage_filename)
    
    with open(file_path, "wb") as buffer:
        buffer.write(file_content)
        
    try:
        doc = fitz.open(file_path)
        page_count = len(doc)
        doc.close()
    except Exception as e:
        logger.error(f"Invalid PDF format: {e}")
        os.remove(file_path)
        raise HTTPException(status_code=415, detail="Invalid physical format corruption detected generically")
        
    pdf_record = PDF(
        id=pdf_id,
        project_id=project_id,
        filename=storage_filename,
        original_name=file.filename,
        file_path=file_path,
        file_hash=file_hash,
        page_count=page_count,
        status=PDFStatus.uploaded
    )
    db.add(pdf_record)
    await db.flush()  # Flush to satisfy FK constraint before inserting job

    # Enqueue a durable ingestion job (idempotent — ON CONFLICT DO NOTHING)
    job_id = uuid.uuid4()
    insert_stmt = pg_insert(IngestionJob).values(
        id=job_id,
        pdf_id=pdf_id,
        project_id=project_id,
        user_id=current_user.id,
        file_path=file_path,
        status=JobStatus.pending,
    ).on_conflict_do_nothing(constraint="uq_ingestion_jobs_pdf_id")
    await db.execute(insert_stmt)
    
    # Implicitly transition to queued after generating Job
    pdf_record.status = PDFStatus.queued
    pdf_record.job_id = job_id
    pdf_record.progress = 5

    await db.commit()
    await db.refresh(pdf_record)
    
    return PDFResponse.model_validate(pdf_record)

@router.get("", response_model=List[PDFResponse])
async def list_pdfs(
    project_id: UUID,
    current_user: User = Depends(get_current_user_clerk),
    db: AsyncSession = Depends(get_db)
):
    await verify_project(project_id, current_user.id, db)
    stmt = select(PDF).where(PDF.project_id == project_id).order_by(PDF.created_at.desc())
    result = await db.execute(stmt)
    pdfs = result.scalars().all()
    return [PDFResponse.model_validate(p) for p in pdfs]

@router.get("/{pdf_id}/status", response_model=PDFResponse)
async def get_pdf_status(
    project_id: UUID,
    pdf_id: UUID,
    current_user: User = Depends(get_current_user_clerk),
    db: AsyncSession = Depends(get_db)
):
    await verify_project(project_id, current_user.id, db)
    stmt = select(PDF).where(PDF.id == pdf_id, PDF.project_id == project_id)
    result = await db.execute(stmt)
    pdf = result.scalar_one_or_none()
    
    if not pdf:
        raise HTTPException(status_code=404, detail="File configurations dynamically unresolved explicitly.")
        
    return PDFResponse.model_validate(pdf)

@router.delete("/{pdf_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pdf(
    project_id: UUID,
    pdf_id: UUID,
    current_user: User = Depends(get_current_user_clerk),
    db: AsyncSession = Depends(get_db)
):
    await verify_project(project_id, current_user.id, db)
    
    stmt = select(PDF).where(PDF.id == pdf_id, PDF.project_id == project_id)
    result = await db.execute(stmt)
    pdf = result.scalar_one_or_none()
    
    if not pdf:
        raise HTTPException(status_code=404, detail="File configurations dynamically unresolved explicitly.")
        
    if os.path.exists(pdf.file_path):
        try:
            os.remove(pdf.file_path)
        except OSError as e:
            logger.warning(f"File physical constraints orphaned locally: {e}")
    else:
        logger.warning(f"Missing logical path execution intrinsically mapped securely: {pdf.file_path}")
        
    from app.services.vector_store import VectorStoreService
    vs = VectorStoreService()
    try:
        vs.delete_by_pdf(str(pdf.id))
    except Exception as e:
         logger.warning(f"Engine connection exception safely logging unhandled vectors globally natively: {e}")
         
    await db.delete(pdf)
    await db.commit()

@router.get("/{pdf_id}/download")
async def download_pdf(
    project_id: UUID,
    pdf_id: UUID,
    current_user: User = Depends(get_current_user_clerk),
    db: AsyncSession = Depends(get_db)
):
    await verify_project(project_id, current_user.id, db)
    stmt = select(PDF).where(PDF.id == pdf_id, PDF.project_id == project_id)
    result = await db.execute(stmt)
    pdf = result.scalar_one_or_none()
    
    if not pdf or not os.path.exists(pdf.file_path):
        raise HTTPException(status_code=404, detail="File natively decoupled or missing from local execution instances explicitly.")
        
    return FileResponse(
        path=pdf.file_path,
        filename=pdf.original_name,
        media_type='application/pdf',
        content_disposition_type="inline"
    )
