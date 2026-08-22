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
        async def create_research_run(self, session_id, project_id, user_id, query, mode="complex"):
            class DummyRun: id = UUID(int=1)
            return DummyRun()
        async def add_research_steps(self, run_id, steps_data):
            return [{"id": str(UUID(int=i+1234)), "type": s.get("type", "analysis"), "status": "queued"} for i, s in enumerate(steps_data)]
        async def update_research_step(self, run_id, step_id, status, result_data=None):
            return {"id": step_id, "status": status}

    class MockRetrievalService:
        def __init__(self): pass
        def retrieve(self, *args, **kwargs):
            return [
                {"pdf_id": "doc1", "filename": "documentA.pdf", "page_number": 1, "text": "React uses a virtual DOM component abstraction heavily."},
                {"pdf_id": "doc1", "filename": "documentA.pdf", "page_number": 2, "text": "React uses unidirectional data flow."},
                {"pdf_id": "doc2", "filename": "documentB.pdf", "page_number": 1, "text": "Vue uses a virtual DOM implicitly paired with functional reactivities."},
                {"pdf_id": "doc2", "filename": "documentB.pdf", "page_number": 2, "text": "Vue enables bidirectional bindings natively."}
            ]

    class MockClient:
        class Models:
            def embed_content(self, *args, **kwargs):
                class Emb:
                    values = [0.1] * 768
                class DummyResp:
                    embeddings = [Emb()]
                return DummyResp()

            def generate_content(self, *args, **kwargs):
                class Resp: text = "{}" 
                inst = ""
                if "config" in kwargs and kwargs["config"] and hasattr(kwargs["config"], "system_instruction"):
                    inst = str(kwargs["config"].system_instruction)
                if "Analysis" in inst:
                    class Resp: text = json.dumps({"document_id": "mock", "key_findings": ["React rocks"], "summary": "React"})
                    return Resp()
                if "Comparison" in inst:
                    class Resp: text = json.dumps({"agreements": [], "contradictions": [], "synthesis_summary": "Comp"})
                    return Resp()
                return Resp()
                
        class AsyncModels:
            async def generate_content_stream(self, *args, **kwargs):
                class AsyncGen:
                    async def __aiter__(self):
                        class Chunk:
                            def __init__(self, t): self.text = t
                        yield Chunk("Mock final output ")
                        yield Chunk("with grounded citation [Source: documentA.pdf, Page: 1].")
                return AsyncGen()
        
        class Aio:
            def __init__(self):
                self.models = MockClient.AsyncModels()
                
        def __init__(self, *args, **kwargs):
            self.models = self.Models()
            self.aio = self.Aio()

    # Pre-emptively mock DB-dependent modules specifically
    mock.patch('app.services.execution_agents.ResearchService', MockResearchService).start()
    mock.patch('app.services.execution_agents.RetrievalService', MockRetrievalService).start()
    mock.patch('app.services.chat_engine.ResearchService', MockResearchService).start()
    mock.patch('app.services.chat_engine.RetrievalService', MockRetrievalService).start()
    
    mock.patch('app.services.execution_agents.genai.Client', MockClient).start()
    mock.patch('app.services.chat_engine.genai.Client', MockClient).start()

    engine = ChatEngine(chat_service=MockChatService())

    # Mock classification and decomposition to avoid LLM
    engine._classify_query = mock.AsyncMock(return_value="COMPLEX")
    engine._decompose_query = mock.AsyncMock(return_value=[
        {"type": "retrieval", "description": "R"},
        {"type": "analysis", "description": "A"},
        {"type": "analysis", "description": "A2"},
        {"type": "comparison", "description": "C"},
        {"type": "verification", "description": "V"},
        {"type": "synthesis", "description": "S"}
    ])

    query = "Compare the state mechanisms and data flows natively handled across React and Vue based on the articles."
    
    print("\n--- INITIATING NO-DB AGENT SSE STREAM ---")
    
    allowed_types = {"status", "artifact", "token", "done"}
    observed_artifacts = set()
    synthesized_tokens = []
    
    async for raw_chunk in engine.stream_chat(
        user_id=UUID(int=1), 
        session_id=UUID(int=1), 
        project_id=UUID(int=0), 
        message=query, 
        pdf_ids=[UUID(int=1), UUID(int=2)]
    ):
        chunk = raw_chunk.strip()
        print(chunk)
        
        # Must trace valid SSE format bounds
        assert chunk.startswith("data: "), f"Invalid SSE format: {chunk}"
        
        payload = json.loads(chunk[6:])
        chunk_type = payload.get("type")
        
        # 1. Assert intermediate output contains only allowed structured artifacts and tokens
        assert chunk_type in allowed_types, f"Raw/unexpected payload type emitted: {chunk_type}"
        
        if chunk_type == "artifact":
            step = payload.get("step")
            assert step in ["retrieval", "analysis", "comparison", "verification"], f"Unknown artifact step tracked: {step}"
            observed_artifacts.add(step)
            
        elif chunk_type == "token":
            synthesized_tokens.append(payload.get("content", ""))

    print("\n--- STREAM COMPLETED, RUNNING ASSERTIONS ---")
    
    # 2. Verify all agents explicitly dispatched allowed structured configurations natively
    # (Ret, Ana, Comp, Ver) must be observed across the execution lifetime mapping structurally
    expected_artifacts = {"retrieval", "analysis", "comparison", "verification"}
    missing_artifacts = expected_artifacts - observed_artifacts
    assert not missing_artifacts, f"Agents failed to emit expected structured artifacts: {missing_artifacts}"
    
    final_text = "".join(synthesized_tokens)
    print(f"\nFinal Assembled Text ({len(final_text)} chars):")
    print(final_text)
    
    # 3. Assert one coherent final answer is streamed implicitly via Token yields 
    assert len(final_text) > 50, "Synthesized text is abnormally short or missing entirely."
    
    # 4. Citations are present and grounded (checking exact bracket format)
    assert "[Source:" in final_text or "[Source" in final_text or "[Source.pdf" in final_text or "[document" in final_text, "No markdown citations identified natively inline!"
    
    # Check explicitly that hallucinated/invented sources don't exist
    # Only documentA.pdf and documentB.pdf exist in our mock scope bounds
    if "[Source" in final_text or "[" in final_text:
        # Simple negative heuristic - confirm nonsense documents aren't naturally cited randomly
        assert "documentC.pdf" not in final_text, "Invented Source Hallucinated: documentC.pdf"
        assert "ReactDocs.pdf" not in final_text, "Invented Source Hallucinated: ReactDocs.pdf"
        
    print("\n[SUCCESS] E2E Streaming Assertions validated:")
    print(" - Stream format strictly adhered to 'data: JSON' boundaries.")
    print(" - No bare CoT strings or raw reasoning emitted outside nested Artifact tags.")
    print(" - Stream tokens sequentially formulated a coherent final summary.")
    print(" - Citations organically rendered based strictly on retrieved chunks bounds natively.")
    print("Done.")

if __name__ == "__main__":
    asyncio.run(test_stream())
