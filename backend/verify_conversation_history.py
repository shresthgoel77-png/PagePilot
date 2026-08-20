import asyncio
import json
import uuid
import os
import sys
from unittest.mock import MagicMock, patch

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from app.services.chat_engine import ChatEngine
from app.models.chat import ChatMessage

async def main():
    # Mock ChatService completely to avoid PostgreSQL
    mock_chat_svc = MagicMock()
    
    # Store messages in memory to simulate DB persistence without schema change
    memory_messages = []
    
    async def mock_get_session_details(session_id, user_id):
        mock_session = MagicMock()
        mock_session.project_id = uuid.UUID("00000000-0000-0000-0000-000000000000")
        return mock_session, list(memory_messages)
        
    async def mock_add_message(session_id, role, content, sources=None):
        msg = ChatMessage(id=uuid.uuid4(), session_id=session_id, role=role, content=content)
        memory_messages.append(msg)
        return msg
        
    mock_chat_svc.get_session_details = mock_get_session_details
    mock_chat_svc.add_message = mock_add_message
    
    with patch("app.services.chat_engine.RetrievalService") as MockRetrievalService:
        mock_retrieval_instance = MagicMock()
        mock_retrieval_instance.retrieve.return_value = [{"pdf_id": "mock_id", "filename": "mock.pdf", "page_number": 1, "text": "Mock text.", "score": 0.99}]
        MockRetrievalService.return_value = mock_retrieval_instance
        
        with patch("app.services.chat_engine.EvidenceVerifier"):
            engine = ChatEngine(mock_chat_svc)
            
            user_id = uuid.uuid4()
            session_id = uuid.uuid4()
            project_id = uuid.UUID("00000000-0000-0000-0000-000000000000")
            
            print("================= TURN 1 =================")
            query_1 = "Describe the results of the MySQL queries."
            print(f"User: {query_1}")
            
            async for chunk in engine.stream_chat(user_id, session_id, project_id, query_1, pdf_ids=[]):
                pass
                
            args, kwargs = mock_retrieval_instance.retrieve.call_args
            print(f"TURN 1 ACTUAL RETRIEVAL QUERY PASSED: {kwargs.get('query')}")
            
            print("\n================= TURN 2 =================")
            query_2 = "What about the second one?"
            print(f"User: {query_2}")
            
            async for chunk in engine.stream_chat(user_id, session_id, project_id, query_2, pdf_ids=[]):
                pass
                
            args, kwargs = mock_retrieval_instance.retrieve.call_args
            print(f"TURN 2 ACTUAL RETRIEVAL QUERY PASSED: {kwargs.get('query')}")
            
            print("\n================= UNRELATED SESSION =================")
            # Switch to a new session (memory_messages is bound to mock, so we clear it for simplicity or use a dict in a real scale)
            memory_messages.clear()
            session_id_2 = uuid.uuid4()
            query_3 = "What about the second one?"
            print(f"User (New Session): {query_3}")
            
            async for chunk in engine.stream_chat(user_id, session_id_2, project_id, query_3, pdf_ids=[]):
                pass
                
            args, kwargs = mock_retrieval_instance.retrieve.call_args
            print(f"UNRELATED SESSION ACTUAL RETRIEVAL QUERY PASSED: {kwargs.get('query')}")

if __name__ == "__main__":
    asyncio.run(main())
