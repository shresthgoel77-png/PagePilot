import asyncio
import sys
import json
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

sys.path.append("c:/Users/HP/OneDrive/Desktop/.vscode/gen ai/backend")

from app.services.chat_engine import ChatEngine
from app.services.chat_service import ChatService

async def main():
    chat_service_mock = MagicMock(spec=ChatService)
    # Mock get_session_details to return valid matching project
    mock_session = MagicMock()
    mock_session.project_id = "test-project-id"
    chat_service_mock.get_session_details = AsyncMock(return_value=(mock_session, []))
    chat_service_mock.add_message = AsyncMock()

    engine = ChatEngine(chat_service_mock)
    
    # Mock _classify_query dynamically
    async def mock_classify(message):
        if "Synthesize" in message:
            return "COMPLEX"
        return "SIMPLE"
    
    engine._classify_query = mock_classify
    
    # Mock retrieval and internal LLM generation for SIMPLE
    engine.retrieval_service = MagicMock()
    engine.retrieval_service.retrieve = MagicMock(return_value=[{"pdf_id": "1", "filename": "test.pdf", "page_number": 1, "text": "context", "score": 0.9}])
    
    engine.client = MagicMock()
    engine.client.aio = MagicMock()
    engine.client.aio.models = AsyncMock()

    # Mock generator stream for SIMPLE
    async def mock_stream_caller(*args, **kwargs):
        async def real_generator():
            class MockChunk:
                def __init__(self, t):
                    self.text = t
            yield MockChunk("This is ")
            yield MockChunk("the simple response.")
        return real_generator()
        
    engine.client.aio.models.generate_content_stream = mock_stream_caller
    engine.evidence_verifier = MagicMock()
    engine.evidence_verifier.verify_claims = MagicMock(return_value={})

    print("\n--- TEST 1: SIMPLE FACTUAL QUESTION ---")
    gen1 = engine.stream_chat(uuid4(), uuid4(), "test-project-id", "What is this document about?", [])
    async for chunk in gen1:
        if "token" in chunk or "status" in chunk:
            print("STREAM:", chunk.strip())
            
    print("\n--- TEST 2: COMPLEX QUESTION ---")
    gen2 = engine.stream_chat(uuid4(), uuid4(), "test-project-id", "Synthesize the main differences in architecture proposed in these three documents and explain the trade-offs in depth.", [])
    async for chunk in gen2:
        if "token" in chunk or "status" in chunk:
            print("STREAM:", chunk.strip())
            
    print("\n--- TEST 3: FALLBACK VALIDATION (API KEY INVALID) ---")
    # Restore original classify to show fallback on exception
    del engine._classify_query
    
    async def mock_throw_error(*args, **kwargs):
        raise Exception("API key not valid")
        
    engine.client.aio.models.generate_content = mock_throw_error
    
    gen3 = engine.stream_chat(uuid4(), uuid4(), "test-project-id", "Some question", [])
    async for chunk in gen3:
        if "status" in chunk:
            print("STREAM:", chunk.strip())

if __name__ == "__main__":
    asyncio.run(main())
