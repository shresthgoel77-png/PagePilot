import asyncio
import uuid
import sys
import os

sys.path.append(os.path.join(os.getcwd(), 'backend'))

from collections import namedtuple
from unittest.mock import Mock, AsyncMock

# Load real env to use Gemini
from dotenv import load_dotenv
load_dotenv(os.path.join(os.getcwd(), '.env'))
import logging
logging.basicConfig(level=logging.ERROR, force=True, format="%(message)s")

from app.services.chat_engine import ChatEngine

SessionMock = namedtuple("SessionMock", ["project_id"])
MessageMock = namedtuple("MessageMock", ["role", "content"])

class MockChatService:
    async def get_session_details(self, session_id, user_id):
        # returns session, db_messages
        return SessionMock(project_id=uuid.UUID(int=1)), []

    async def add_message(self, session_id, role, content, sources=None):
        pass

class MockRetrievalService:
    def __init__(self, mode="in_corpus"):
        self.mode = mode
        
    def retrieve(self, project_id, query, top_k, final_k, pdf_ids):
        if self.mode == "out_corpus":
            return []
        
        return [{
            "pdf_id": str(uuid.UUID(int=3)),
            "filename": "algorithm_paper.pdf",
            "page_number": 42,
            "text": "The key algorithm discussed is the Advanced Reranker, which optimizes vector search explicitly.",
            "score": 0.99
        }]

async def main():
    chat_service = MockChatService()
    
    # Needs a real API key to invoke gemini
    # the environment variable is loaded by settings. We should parse .env manually if needed, 
    # but I'll dynamically load it from .env for the real test:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.getcwd(), '.env'))

    print("\n\n=== Test 1: Out of Corpus Question ===")
    from app.services import chat_engine
    chat_engine.RetrievalService = lambda: MockRetrievalService(mode="out_corpus")
    engine = ChatEngine(chat_service=chat_service)
    
    user_id = uuid.UUID(int=1)
    session_id = uuid.UUID(int=2)
    project_id = uuid.UUID(int=1)
    
    gen = engine.stream_chat(user_id, session_id, project_id, "What is the capital of France?")
    
    result = []
    async for chunk in gen:
        # chunks are like: data: {"type": "token", "content": "..."}
        result.append(chunk)
        
    print("".join(result))

    print("\n\n=== Test 2: In Corpus Question ===")
    
    chat_engine.RetrievalService = lambda: MockRetrievalService(mode="in_corpus")
    engine2 = ChatEngine(chat_service=chat_service)
    gen2 = engine2.stream_chat(user_id, session_id, project_id, "What is the key algorithm discussed? Please cite based on constraints.")
    
    result2 = []
    async for chunk in gen2:
        result2.append(chunk)
        
    print("".join(result2))

if __name__ == "__main__":
    asyncio.run(main())
