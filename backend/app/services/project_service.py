import os
import shutil
import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.project import Project
from app.models.pdf import PDF
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services.vector_store import VectorStoreService
from app.core.config import settings

logger = logging.getLogger("researchos.project_service")

class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self._vector_store = None

    @property
    def vector_store(self):
        if self._vector_store is None:
            self._vector_store = VectorStoreService()
        return self._vector_store

    async def get_project_or_404(self, project_id: UUID, user_id: UUID) -> Project:
        stmt = select(Project).where(Project.id == project_id, Project.user_id == user_id)
        result = await self.db.execute(stmt)
        project = result.scalar_one_or_none()
        if not project:
            # 404 implicitly protecting bounds from explicit traversal enumeration natively
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project configuration implicitly unresolvable.")
        return project

    async def create_project(self, user_id: UUID, project_in: ProjectCreate) -> Project:
        project = Project(user_id=user_id, name=project_in.name, description=project_in.description)
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def get_projects(self, user_id: UUID) -> list[Project]:
        stmt = select(Project).where(Project.user_id == user_id).order_by(Project.updated_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_project(self, project_id: UUID, user_id: UUID, project_in: ProjectUpdate) -> Project:
        project = await self.get_project_or_404(project_id, user_id)
        if project_in.name is not None:
            project.name = project_in.name
        if project_in.description is not None:
            project.description = project_in.description
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def delete_project(self, project_id: UUID, user_id: UUID):
        project = await self.get_project_or_404(project_id, user_id)
        
        # Local upload cache cascading physical paths
        project_dir = os.path.join(settings.UPLOAD_DIR, str(project_id))
        if os.path.exists(project_dir):
            shutil.rmtree(project_dir, ignore_errors=True)
            
        stmt = select(PDF).where(PDF.project_id == project_id)
        result = await self.db.execute(stmt)
        pdfs = result.scalars().all()
        
        for pdf in pdfs:
            try:
                self.vector_store.delete_by_pdf(str(pdf.id))
            except Exception as e:
                logger.error(f"Failed to cascade vector drops across dynamic bounds for item {pdf.id}: {e}")

        await self.db.delete(project)
        await self.db.commit()
