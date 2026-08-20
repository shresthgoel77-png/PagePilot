import asyncio
import uuid
import sys
import os
import json

sys.path.append(os.path.join(os.getcwd(), 'backend'))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.getcwd(), '.env'))

if not os.getenv("GEMINI_API_KEY"):
    raise RuntimeError("GEMINI_API_KEY is missing from the environment. Please set it in your local .env file.")

from app.services.chat_engine import ChatEngine
from app.services.evidence_verifier import EvidenceVerifier
from collections import namedtuple

SessionMock = namedtuple("SessionMock", ["project_id"])

class MockChatService:
    async def get_session_details(self, session_id, user_id):
        return SessionMock(project_id=uuid.UUID(int=1)), []
    async def add_message(self, session_id, role, content, sources=None):
        pass

class MockRetrievalService:
    def retrieve(self, project_id, query, top_k, final_k, pdf_ids):
        # Return realistic context
        return [{
            "pdf_id": str(uuid.UUID(int=3)),
            "filename": "geography_factsheet.pdf",
            "page_number": 1,
            "text": "The capital of France is Paris. It is known for the Eiffel Tower.",
            "score": 0.99
        }]

class MockGeminiResponse:
    def __init__(self, text):
        self.text = text

class MockStream:
    def __init__(self, items):
        self.items = items
    async def __aiter__(self):
        for i in self.items:
            yield i

async def mock_generate_content_stream(*args, **kwargs):
    return MockStream([
        MockGeminiResponse("The capital of France is "),
        MockGeminiResponse("Paris [Source: geography_factsheet.pdf, Page 1]. "),
        MockGeminiResponse("However, Neo-Tokyo is """ + "the capital of Mars. "),
        MockGeminiResponse("This is widely known in sci-fi novels.")
    ])

async def run_verification_test():
    print("\n=== Post-Generation Evidence Verification Test ===")
    
    chat_service = MockChatService()
    engine = ChatEngine(chat_service=chat_service)
    
    # Needs actual embeddings locally to verify!
    engine.retrieval_service = MockRetrievalService()
    
    user_id = uuid.UUID(int=1)
    session_id = uuid.UUID(int=2)
    project_id = uuid.UUID(int=1)
    
    # Mocking Gemini SDK precisely
    engine.client.aio.models.generate_content_stream = mock_generate_content_stream
    
    gen = engine.stream_chat(user_id, session_id, project_id, "What are the capitals of France and Mars?")
    
    print("Capturing SSE Streams:")
    async for chunk in gen:
        print(chunk.strip())

if __name__ == "__main__":
    asyncio.run(run_verification_test())
