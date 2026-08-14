from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from pydantic import BaseModel
from app.db.session import get_db
from app.models.user import User
from app.core.clerk_auth import get_current_user_clerk
from app.services.gap_engine import GapAnalysisEngine, GapAnalysisResponse

router = APIRouter(prefix="/projects", tags=["gap_finder"])

class GapAnalysisRequest(BaseModel):
    focus_area: Optional[str] = None
    session_id: Optional[str] = None

def get_gap_engine(db: AsyncSession = Depends(get_db)) -> GapAnalysisEngine:
    return GapAnalysisEngine(db)

@router.post("/{project_id}/gaps", response_model=GapAnalysisResponse)
async def extract_gaps(
    project_id: str,
    request: GapAnalysisRequest,
    current_user: User = Depends(get_current_user_clerk),
    engine: GapAnalysisEngine = Depends(get_gap_engine)
):
    return await engine.execute_gap_analysis(
        user_id=current_user.id,
        project_id=project_id,
        focus_area=request.focus_area,
        session_id=request.session_id
    )
