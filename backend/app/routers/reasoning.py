from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional
import json

from app.db.session import get_db
from app.models.user import User
from app.core.deps import get_current_user
from app.services.reasoning_engine import ReasoningEngine

router = APIRouter(prefix="/projects", tags=["reasoning"])

class ReasoningRequest(BaseModel):
    query: str
    pdf_ids: List[str]
    mode: str = "compare"
    session_id: Optional[str] = None

def get_reasoning_engine(db: AsyncSession = Depends(get_db)) -> ReasoningEngine:
    return ReasoningEngine(db)

@router.post("/{project_id}/reason")
async def execute_reasoning(
    project_id: str,
    request_data: ReasoningRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    engine: ReasoningEngine = Depends(get_reasoning_engine)
):
    if request_data.mode == "compare" and len(request_data.pdf_ids) < 2:
        raise HTTPException(status_code=400, detail="Comparison execution fundamentally requires at least 2 distinct physical limits mapping structurally.")
        
    async def event_generator():
        async for chunk in engine.execute_multi_paper_synthesis(
            user_id=current_user.id,
            project_id=project_id,
            query=request_data.query,
            pdf_ids=request_data.pdf_ids,
            mode=request_data.mode,
            session_id=request_data.session_id
        ):
            if await request.is_disconnected():
                break
            yield chunk

    return StreamingResponse(event_generator(), media_type="text/event-stream")
