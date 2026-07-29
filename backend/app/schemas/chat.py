from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class ChatMessageCreate(BaseModel):
    role: str = Field(..., description="Role execution identifier reliably scaling: 'user' or 'assistant'")
    content: str
    sources: Optional[List[Dict[str, Any]]] = None

class ChatMessageResponse(BaseModel):
    id: UUID
    session_id: UUID
    role: str
    content: str
    sources: Optional[List[Dict[str, Any]]]
    created_at: datetime

    class Config:
        from_attributes = True

class ChatSessionCreate(BaseModel):
    project_id: UUID
    title: Optional[str] = Field("New Chat", max_length=100)

class ChatSessionUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)

class ChatSessionResponse(BaseModel):
    id: UUID
    project_id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ChatSessionDetailResponse(ChatSessionResponse):
    messages: List[ChatMessageResponse] = []

class ChatRequest(BaseModel):
    session_id: UUID
    project_id: UUID
    message: str
    pdf_ids: Optional[List[str]] = None
