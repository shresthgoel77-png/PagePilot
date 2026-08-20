import asyncio
import uuid
import sys
import os
import json

sys.path.append(os.path.join(os.getcwd(), 'backend'))

from unittest.mock import patch
from dotenv import load_dotenv

load_dotenv(os.path.join(os.getcwd(), '.env'))

if not os.getenv("GEMINI_API_KEY"):
    raise RuntimeError("GEMINI_API_KEY is missing from the environment. Please set it in your local .env file.")

from app.services.chat_engine import ChatEngine
from collections import namedtuple

SessionMock = namedtuple("SessionMock", ["project_id"])

class MockChatService:
    async def get_session_details(self, session_id, user_id):
        return SessionMock(project_id=uuid.UUID(int=1)), []
    async def add_message(self, session_id, role, content, sources=None):
        pass

class MockRetrievalService:
    def __init__(self, mode="no_evidence"):
        self.mode = mode
    def retrieve(self, project_id, query, top_k, final_k, pdf_ids):
        if self.mode == "no_evidence":
            return []
        
        chunks = []
        if self.mode == "partial_evidence" or self.mode == "one_source":
            chunks.append({
                "pdf_id": str(uuid.UUID(int=3)),
                "filename": "database_schema.pdf",
                "page_number": 1,
                "text": "The database schema has a users table and a projects table. Nothing about geography here.",
                "score": 0.99
            })
        if self.mode == "multiple_sources":
            chunks.append({
                "pdf_id": str(uuid.UUID(int=3)),
                "filename": "database_schema.pdf",
                "page_number": 1,
                "text": "The database schema has a users table and a projects table. Nothing about geography here.",
                "score": 0.99
            })
            chunks.append({
                "pdf_id": str(uuid.UUID(int=4)),
                "filename": "system_design.pdf",
                "page_number": 12,
                "text": "The architecture is split into microservices, communicating via Kafka.",
                "score": 0.99
            })
        return chunks

async def run_test(engine, user_id, session_id, project_id, mode, query):
    print(f"\n=== Test: {mode} ===")
    print(f"Query: {query}")
    
    from app.services import chat_engine
    chat_engine.RetrievalService = lambda: MockRetrievalService(mode=mode)
    
    engine.retrieval_service = MockRetrievalService(mode=mode)
    
    original_stream = engine.client.aio.models.generate_content_stream
    async def patched_stream(*args, **kwargs):
        if kwargs.get('model') == 'gemini-2.5-flash':
            kwargs['model'] = 'gemini-3.6-flash'
        return await original_stream(*args, **kwargs)
    
    engine.client.aio.models.generate_content_stream = patched_stream
    
    gen = engine.stream_chat(user_id, session_id, project_id, query)
    
    result = []
    async for chunk in gen:
        result.append(chunk)
    
    res = "".join(result)
    print("Output Stream:")
    print(res)

async def main():
    chat_service = MockChatService()
    engine = ChatEngine(chat_service=chat_service)
    
    user_id = uuid.UUID(int=1)
    session_id = uuid.UUID(int=2)
    project_id = uuid.UUID(int=1)
    
    await run_test(engine, user_id, session_id, project_id, "no_evidence", "What is the capital of France?")
    await run_test(engine, user_id, session_id, project_id, "partial_evidence", "What is the capital of France?")
    await run_test(engine, user_id, session_id, project_id, "one_source", "What tables are in the database schema?")
    await run_test(engine, user_id, session_id, project_id, "multiple_sources", "Describe the database schema AND the architecture communication.")

if __name__ == "__main__":
    asyncio.run(main())
