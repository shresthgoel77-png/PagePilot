import sys
import os
import uuid
import json
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.chat_engine import ChatEngine
from google.genai import types

async def main():
    print("\n--- Verifying Chat States ---\n")
    
    # Common Mock Environment
    mock_chat_svc = AsyncMock()
    class DummySession:
        project_id = uuid.UUID('12345678-1234-5678-1234-567812345678')
    mock_chat_svc.get_session_details.return_value = (DummySession(), [])
    mock_chat_svc.add_message.return_value = AsyncMock(id=uuid.uuid4())
    
    engine = ChatEngine(chat_service=mock_chat_svc)
    
    project_id = DummySession.project_id
    session_id = uuid.uuid4()
    user_id = uuid.uuid4()
    
    # 1. VERIFY EMPTY PROJECT / NO CHUNKS
    print("\n[Test 1] Emulating Empty Project (0 chunks returned)")
    with patch.object(engine.retrieval_service, 'retrieve', return_value=[]):
        generator = engine.stream_chat(user_id, session_id, project_id, "Hello")
        
        events = []
        async for chunk in generator:
            if chunk.startswith("data: "):
                events.append(json.loads(chunk.replace("data: ", "", 1).strip()))
                
        # Status retrieving -> Error no evidence
        assert events[0] == {'type': 'status', 'content': 'retrieving'}, "Missing retrieving status"
        assert events[1]['type'] == 'error' and 'No relevant evidence found' in events[1]['content'], "Missing explicit No Evidence chunk"
        print("✅ Test 1 Passed: Distinct Empty Project error emitted.")

    # 2. VERIFY RETRIEVAL CRASH
    print("\n[Test 2] Emulating Retrieval Timeout / Fault")
    def mock_retrieve_fault(*args, **kwargs):
        raise TimeoutError("Qdrant socket timeout simulated")
        
    with patch.object(engine.retrieval_service, 'retrieve', side_effect=mock_retrieve_fault):
        generator = engine.stream_chat(user_id, session_id, project_id, "Hello")
        
        events = []
        async for chunk in generator:
            if chunk.startswith("data: "):
                events.append(json.loads(chunk.replace("data: ", "", 1).strip()))
                
        # Status retrieving -> Error retrieval fault
        assert events[0] == {'type': 'status', 'content': 'retrieving'}, "Missing retrieving status"
        assert events[1]['type'] == 'error' and 'Retrieval failed structurally: Qdrant socket timeout simulated' in events[1]['content'], "Missing distinct retrieval fault"
        print("✅ Test 2 Passed: Distinct Retrieval Crash error explicitly bounded.")
        
    # 3. VERIFY GENERATION CRASH
    print("\n[Test 3] Emulating Generation Fault (LLM limits/crash)")
    with patch.object(engine.retrieval_service, 'retrieve', return_value=[{"pdf_id": str(uuid.uuid4()), "filename": "X.pdf", "page_number": 1, "text": "Dummy text"}]):
        
        async def mock_gen_crash(*args, **kwargs):
            raise ConnectionError("Gemini API Rate Limit Exceeded")
            yield  # required to make it an async generator if we were yielding, but raising instantly is fine
            
        engine.client.aio.models.generate_content_stream = mock_gen_crash
        
        generator = engine.stream_chat(user_id, session_id, project_id, "Hello")
        
        events = []
        async for chunk in generator:
            if chunk.startswith("data: "):
                events.append(json.loads(chunk.replace("data: ", "", 1).strip()))
                
        print(f"DEBUG TEST 3 EVENTS: {events}")
        
        assert events[0] == {'type': 'status', 'content': 'retrieving'}, "Missing retrieving status"
        assert events[1] == {'type': 'status', 'content': 'generating'}, "Missing generating status"
        assert events[2]['type'] == 'error' and 'Generation failed structurally:' in events[2]['content'], "Missing specific LLM crash trace"
        
        print("✅ Test 3 Passed: Distinct LLM failure trace uniquely identified natively.")
        
    print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(main())
