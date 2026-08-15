from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.user import User
from app.schemas.chat import ChatRequest
from app.services.chat_service import ChatService
from app.services.chat_engine import ChatEngine
from app.core.clerk_auth import get_current_user_clerk

router = APIRouter(prefix="/chat", tags=["chat_engine"])

def get_chat_engine(db: AsyncSession = Depends(get_db)) -> ChatEngine:
    chat_svc = ChatService(db)
    return ChatEngine(chat_service=chat_svc)

@router.post("/stream")
async def chat_stream(
    request: Request,
    payload: ChatRequest,
    current_user: User = Depends(get_current_user_clerk),
    engine: ChatEngine = Depends(get_chat_engine)
):
    async def event_generator():
        # Execute dynamically routed LangChain structures encapsulating native state explicitly bypassing sync logic globally securely inherently locally 
        async for chunk in engine.stream_chat(
            user_id=current_user.id,
            session_id=payload.session_id,
            project_id=payload.project_id,
            message=payload.message,
            pdf_ids=payload.pdf_ids
        ):
            if await request.is_disconnected():
                break
            yield chunk

    # Mount Streaming format definitively resolving explicitly uniquely capturing loops gracefully tracking execution securely 
    return StreamingResponse(event_generator(), media_type="text/event-stream")
