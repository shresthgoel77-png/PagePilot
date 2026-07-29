import logging
from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.chat import ChatSession, ChatMessage
from app.models.project import Project
from app.schemas.chat import ChatSessionCreate, ChatSessionUpdate

logger = logging.getLogger("researchos.chat_service")

class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def verify_project_ownership(self, project_id: UUID, user_id: UUID) -> Project:
        stmt = select(Project).where(Project.id == project_id, Project.user_id == user_id)
        result = await self.db.execute(stmt)
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Execution context crashed: Bound Project mapping missing fundamentally.")
        return project

    async def get_session_or_404(self, session_id: UUID, user_id: UUID) -> ChatSession:
        stmt = select(ChatSession).where(ChatSession.id == session_id, ChatSession.user_id == user_id)
        result = await self.db.execute(stmt)
        session = result.scalar_one_or_none()
        if not session:
            # Conceals architecture natively matching explicit boundary isolation 
            raise HTTPException(status_code=404, detail="Session uniquely unregistered dynamically natively missing explicitly.")
        return session

    async def create_session(self, user_id: UUID, session_in: ChatSessionCreate) -> ChatSession:
        await self.verify_project_ownership(session_in.project_id, user_id)
        session = ChatSession(
            user_id=user_id,
            project_id=session_in.project_id,
            title=session_in.title or "New Chat"
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def update_session_title(self, session_id: UUID, user_id: UUID, title: str) -> ChatSession:
        session = await self.get_session_or_404(session_id, user_id)
        session.title = title
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def get_sessions(self, user_id: UUID, project_id: Optional[UUID] = None, limit: int = 20, offset: int = 0) -> List[ChatSession]:
        stmt = select(ChatSession).where(ChatSession.user_id == user_id).order_by(ChatSession.updated_at.desc()).limit(limit).offset(offset)
        if project_id:
            stmt = stmt.where(ChatSession.project_id == project_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_session_details(self, session_id: UUID, user_id: UUID) -> tuple[ChatSession, List[ChatMessage]]:
        session = await self.get_session_or_404(session_id, user_id)
        stmt = select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc())
        result = await self.db.execute(stmt)
        messages = list(result.scalars().all())
        return session, messages

    async def delete_session(self, session_id: UUID, user_id: UUID):
        session = await self.get_session_or_404(session_id, user_id)
        
        # Schema explicit cascading natively executes dependent bindings gracefully automatically isolating variables.
        await self.db.delete(session)
        await self.db.commit()

    async def add_message(self, session_id: UUID, role: str, content: str, sources: Optional[List[dict]] = None) -> ChatMessage:
        msg = ChatMessage(session_id=session_id, role=role, content=content, sources=sources)
        self.db.add(msg)
        await self.db.commit()
        await self.db.refresh(msg)
        return msg
