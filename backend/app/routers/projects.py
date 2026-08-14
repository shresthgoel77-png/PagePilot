from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.services.project_service import ProjectService
from app.core.clerk_auth import get_current_user_clerk

router = APIRouter(prefix="/projects", tags=["projects"])

def get_project_service(db: AsyncSession = Depends(get_db)) -> ProjectService:
    return ProjectService(db)

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_in: ProjectCreate,
    current_user: User = Depends(get_current_user_clerk),
    service: ProjectService = Depends(get_project_service)
):
    return await service.create_project(current_user.id, project_in)

@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    current_user: User = Depends(get_current_user_clerk),
    service: ProjectService = Depends(get_project_service)
):
    return await service.get_projects(current_user.id)

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user_clerk),
    service: ProjectService = Depends(get_project_service)
):
    return await service.get_project_or_404(project_id, current_user.id)

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_in: ProjectUpdate,
    current_user: User = Depends(get_current_user_clerk),
    service: ProjectService = Depends(get_project_service)
):
    return await service.update_project(project_id, current_user.id, project_in)

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user_clerk),
    service: ProjectService = Depends(get_project_service)
):
    await service.delete_project(project_id, current_user.id)
