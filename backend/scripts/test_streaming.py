import asyncio
import os
import sys
import logging
import json
from uuid import UUID

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import .env manually like test_agents.py
from dotenv import dotenv_values
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
env_dict = dotenv_values(dotenv_path)
if "GEMINI_API_KEY" in env_dict:
    os.environ["GEMINI_API_KEY"] = env_dict["GEMINI_API_KEY"].strip()

import unittest.mock as mock
from app.services.chat_engine import ChatEngine

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("test_streaming")

async def test_stream():
    class MockSession:
        project_id = UUID(int=0)
        id = UUID(int=1)

    class MockChatService:
        async def get_session_details(self, session_id, user_id):
            return MockSession(), []
        async def add_message(self, *args, **kwargs):
            class MockMsg:
                id = UUID(int=2)
            return MockMsg()

    class MockResearchStep:
        def __init__(self, step_id, step_type):
            self.id = step_id
            self.step_type = step_type
            self.status = "completed"
            self.result = "{}"
            
    class MockResearchService:
        async def create_research_run(self, session_id, query):
            class DummyRun: id = UUID(int=1)
            return DummyRun()
        async def add_research_steps(self, run_id, steps_data):
            return [MockResearchStep(UUID(int=i+1234), s["type"]) for i, s in enumerate(steps_data)]
        async def update_research_step(self, step_id, status, result_data=None):
            pass

    class MockRetrievalService:
        def __init__(self): pass
        def retrieve(self, *args, **kwargs):
            return [
                {"pdf_id": "doc1", "filename": "documentA.pdf", "page_number": 1, "text": "React uses a virtual DOM component abstraction heavily."},
                {"pdf_id": "doc1", "filename": "documentA.pdf", "page_number": 2, "text": "React uses unidirectional data flow."},
                {"pdf_id": "doc2", "filename": "documentB.pdf", "page_number": 1, "text": "Vue uses a virtual DOM implicitly paired with functional reactivities."},
                {"pdf_id": "doc2", "filename": "documentB.pdf", "page_number": 2, "text": "Vue enables bidirectional bindings natively."}
            ]

    # Pre-emptively mock DB-dependent modules specifically
    mock.patch('app.services.execution_agents.ResearchService', MockResearchService).start()
    mock.patch('app.services.execution_agents.RetrievalService', MockRetrievalService).start()
    mock.patch('app.services.chat_engine.ResearchService', MockResearchService).start()
    mock.patch('app.services.chat_engine.RetrievalService', MockRetrievalService).start()

    engine = ChatEngine(chat_service=MockChatService())

    # Mock classification to guarantee COMPLEX loop execution logic
    engine._classify_query = mock.AsyncMock(return_value="COMPLEX")

    query = "Compare the state mechanisms and data flows natively handled across React and Vue based on the articles."
    
    print("\n--- INITIATING NO-DB AGENT SSE STREAM ---")
    async for chunk in engine.stream_chat(
        user_id=UUID(int=1), 
        session_id=UUID(int=1), 
        project_id=UUID(int=0), 
        message=query, 
        pdf_ids=[UUID(int=1), UUID(int=2)]
    ):
        print(f"{chunk.strip()}")

if __name__ == "__main__":
    asyncio.run(test_stream())
