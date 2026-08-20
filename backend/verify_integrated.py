import asyncio
import os
import sys
import uuid
import json

# Setup in-memory qdrant BEFORE importing the app
os.environ["QDRANT_URL"] = ":memory:"
os.environ["QDRANT_API_KEY"] = ""

from dotenv import load_dotenv
load_dotenv(".env") # still load the api key

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from unittest.mock import MagicMock, patch
from app.models.chat import ChatMessage
import app.db.qdrant as qdrant_module
from qdrant_client import QdrantClient

# Override Qdrant connection to actually be memory-bound instead of HTTP
qdrant_module.qdrant_client = QdrantClient(location=":memory:") 

from app.services.chat_engine import ChatEngine
from app.services.vector_store import VectorStoreService

async def main():
    print("Initializing in-memory databases integration...")
    
    # Init Qdrant Collection
    qdrant_module.ensure_collection()
    
    # Insert some dummy chunks into Qdrant for Retrieval to find
    vstore = VectorStoreService()
    project_uuid_str = str(uuid.UUID(int=1))
    mock_pdf_id = str(uuid.UUID(int=2))
    
    dummy_chunks = [
        {
            "vector": [0.1] * 3072, # gemini embedding size roughly
            "payload": {
                "project_id": project_uuid_str,
                "pdf_id": mock_pdf_id,
                "page_number": 1,
                "chunk_index": 1,
                "text": "The first MySQL query optimized indexes. The second one dropped unused tables.",
                "filename": "mysql_optimizations.pdf",
                "type": "chunk",
                "is_ocr": False
            }
        }
    ]
    
    print("Upserting dummy data to in-memory Qdrant...")
    vstore.upsert_chunks(dummy_chunks)

    # Mock ChatService completely to avoid PostgreSQL
    mock_chat_svc = MagicMock()
    memory_messages = []
    
    async def mock_get_session_details(session_id, user_id):
        mock_session = MagicMock()
        mock_session.project_id = uuid.UUID(project_uuid_str)
        return mock_session, list(memory_messages)
        
    async def mock_add_message(session_id, role, content, sources=None):
        msg = ChatMessage(id=uuid.uuid4(), session_id=session_id, role=role, content=content)
        memory_messages.append(msg)
        return msg
        
    mock_chat_svc.get_session_details = mock_get_session_details
    mock_chat_svc.add_message = mock_add_message

    # DO NOT MOCK EvidenceVerifier or RetrievalService - Full integration
    engine_svc = ChatEngine(mock_chat_svc)
    
    user_id = uuid.uuid4()
    session_id = uuid.uuid4()
    project_id = uuid.UUID(project_uuid_str)
    
    # Wrap the client to intercept SDK properties that spawn new async model objects
    class ClientWrapper:
        def __init__(self, real_client):
            self.real_client = real_client
            self.aio = self.MockAIO(real_client)
            self.models = real_client.models
            
        class MockAIO:
            def __init__(self, real_client):
                # Retrieve the original real AsyncModels via the property getter
                self.models = self.MockModels(type(real_client).aio.fget(real_client).models)
                
            class MockModels:
                def __init__(self, real_models):
                    self.real_models = real_models
                async def generate_content(self, *args, **kwargs):
                    # API models missing locally, returning dummy reformulation
                    class MockResp:
                        text = "What were the results of the second MySQL query?"
                    return MockResp()
                    
                async def generate_content_stream(self, *args, **kwargs):
                    class StreamIterable:
                        async def __aiter__(self):
                            yield type("C", (), {"text": "I "})()
                            yield type("C", (), {"text": "am "})()
                            yield type("C", (), {"text": "a "})()
                            yield type("C", (), {"text": "mock."})()
                    return StreamIterable()

    engine_svc.client = ClientWrapper(engine_svc.client)

    print("\n================= TURN 1 =================")
    query_1 = "Describe the results of the MySQL queries."
    print(f"User: {query_1}")
    
    with patch('app.services.embeddings.EmbeddingService') as MockEmbedder:
        
        mock_inst = MockEmbedder.return_value
        mock_inst.generate_embeddings.return_value = [[0.1] * 3072]
        
        response_1 = ""
        async for chunk in engine_svc.stream_chat(user_id, session_id, project_id, query_1, pdf_ids=[]):
            if chunk.startswith("data: "):
                try:
                    data = json.loads(chunk[6:])
                    if data.get("type") == "token":
                        response_1 += data.get("content", "")
                except:
                    pass
        print(f"Assistant: {response_1}")
        
        print("\n================= TURN 2 =================")
        query_2 = "What about the second one?"
        print(f"User: {query_2}")
        
        response_2 = ""
        async for chunk in engine_svc.stream_chat(user_id, session_id, project_id, query_2, pdf_ids=[]):
            if chunk.startswith("data: "):
                try:
                    data = json.loads(chunk[6:])
                    if data.get("type") == "token":
                        response_2 += data.get("content", "")
                except:
                    pass
        print(f"Assistant: {response_2}")
        
        print("\n================= UNRELATED SESSION =================")
        memory_messages.clear()
        session_id_2 = uuid.uuid4()
        query_3 = "What about the second one?"
        print(f"User (New Session): {query_3}")
        
        response_3 = ""
        async for chunk in engine_svc.stream_chat(user_id, session_id_2, project_id, query_3, pdf_ids=[]):
            if chunk.startswith("data: "):
                try:
                    data = json.loads(chunk[6:])
                    if data.get("type") == "token":
                        response_3 += data.get("content", "")
                except:
                    pass
        print(f"Assistant: {response_3}")

if __name__ == "__main__":
    asyncio.run(main())
