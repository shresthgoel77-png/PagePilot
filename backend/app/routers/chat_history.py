from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.user import User
from app.schemas.chat import ChatSessionCreate, ChatSessionResponse, ChatSessionDetailResponse, ChatSessionUpdate, ChatMessageResponse
from app.services.chat_service import ChatService
from app.core.clerk_auth import get_current_user_clerk

router = APIRouter(prefix="/chat-sessions", tags=["chat_history"])

def get_chat_service(db: AsyncSession = Depends(get_db)) -> ChatService:
    return ChatService(db)

@router.post("/", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    session_in: ChatSessionCreate,
    current_user: User = Depends(get_current_user_clerk),
    service: ChatService = Depends(get_chat_service)
):
    return await service.create_session(current_user.id, session_in)

@router.get("/", response_model=List[ChatSessionResponse])
async def list_chat_sessions(
    project_id: Optional[UUID] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user_clerk),
    service: ChatService = Depends(get_chat_service)
):
    return await service.get_sessions(current_user.id, project_id, limit, offset)

@router.get("/{session_id}", response_model=ChatSessionDetailResponse)
async def get_chat_session_details(
    session_id: UUID,
    current_user: User = Depends(get_current_user_clerk),
    service: ChatService = Depends(get_chat_service)
):
    session, messages = await service.get_session_details(session_id, current_user.id)
    response = ChatSessionDetailResponse.model_validate(session)
    response.messages = [ChatMessageResponse.model_validate(m) for m in messages]
    return response

@router.put("/{session_id}", response_model=ChatSessionResponse)
async def update_chat_session(
    session_id: UUID,
    session_in: ChatSessionUpdate,
    current_user: User = Depends(get_current_user_clerk),
    service: ChatService = Depends(get_chat_service)
):
    return await service.update_session_title(session_id, current_user.id, session_in.title)

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user_clerk),
    service: ChatService = Depends(get_chat_service)
):
    await service.delete_session(session_id, current_user.id)
