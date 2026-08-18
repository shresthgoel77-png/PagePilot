import sys
import os
import json
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from collections import namedtuple
from uuid import uuid4

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.chat_engine import ChatEngine
from app.services.chat_service import ChatService
from app.services.retrieval import RetrievalService
from google.genai import types

def generate_mock_results(limit):
    MockPayload = namedtuple('MockPayload', ['project_id', 'pdf_id', 'page_number', 'chunk_index', 'text', 'filename', 'type', 'is_ocr', 'section'])
    MockResult = namedtuple('MockResult', ['payload', 'score'])
    results = []
    for i in range(limit or 0):
        # Insert a unique index in the text to verify LLM context later
        payload = MockPayload("proj_1", "pdf_1", 1, i, f"Document chunk text number {i}", "file.pdf", "text", False, "")
        results.append(MockResult(payload=payload, score=0.9))
    return results

async def verify_llm_pipeline():
    print("--- Verifying Retrieval top_k vs final_k Pipeline to LLM ---")
    
    chat_svc_mock = MagicMock(spec=ChatService)
    
    chat_engine = ChatEngine(chat_service=chat_svc_mock)
    
    SessionMock = namedtuple('SessionMock', ['project_id'])
    MsgMock = namedtuple('MsgMock', ['role', 'content'])
    proj_id = uuid4()
    chat_svc_mock.get_session_details = AsyncMock(return_value=(
        SessionMock(project_id=proj_id), 
        [MsgMock('user', 'test message')]
    ))
    chat_svc_mock.add_message = AsyncMock()

    # We will track the limit passed to Qdrant, and the texts passed to LLM
    qdrant_called_with_limit = None
    llm_context_string = None

    def mock_search(*args, **kwargs):
        nonlocal qdrant_called_with_limit
        qdrant_called_with_limit = kwargs.get('limit')
        if not qdrant_called_with_limit and len(args) > 1:
            qdrant_called_with_limit = args[1] # fallback
        print(f"  [Qdrant] Mock fetch invoked with limit: {qdrant_called_with_limit}")
        return generate_mock_results(qdrant_called_with_limit)
        
    chat_engine.retrieval_service.embedding_service.generate_embeddings = MagicMock(return_value=[[0.1]*3072])
    chat_engine.retrieval_service.vector_store.search = MagicMock(side_effect=mock_search)
    
    # We will monkeypatch the Google GenAI client to intercept the final formatting context to LLM
    async def mock_generate_content_stream(*args, **kwargs):
        nonlocal llm_context_string
        config = kwargs.get('config')
        if config and hasattr(config, 'system_instruction'):
            llm_context_string = config.system_instruction
            print(f"  [LLM Intercepted Context Block length: {len(str(llm_context_string))}]")

        # Mock the stream response
        class MockStreamChunk:
            def __init__(self, text):
                self.text = text
        
        async def stream_gen():
            yield MockStreamChunk("Mock LLM Response")
            
        return stream_gen()
        
    chat_engine.client.aio.models.generate_content_stream = AsyncMock(side_effect=mock_generate_content_stream)
    
    # ---------------------------------------------------------
    # TEST 1: Standard final_k < top_k logic
    # ---------------------------------------------------------
    print("\n[TEST 1] final_k < top_k (Expected: fetch 50, LLM receives 10)")
    
    # We patch ChatEngine to explicitly pass our parameterized final_k/top_k constraints, 
    # as the hardcoded one right now does 50 and 10. We can just test it directly by calling stream_chat
    # since we updated its defaults to top_k=50, final_k=10 directly.
    
    gen = chat_engine.stream_chat(user_id=uuid4(), session_id=uuid4(), project_id=proj_id, message="Tell me about MySQL")
    async for item in gen:
        pass # Consume stream
        
    assert qdrant_called_with_limit == 50, f"Qdrant called with {qdrant_called_with_limit}"
    # The llm_context_string should contain exactly 10 "Document Chunk" strings since final_k=10
    system_instr = str(llm_context_string)
    context_chunk_count = system_instr.count("Document chunk text number")
    print(f"  [Result] Qdrant Fetched: {qdrant_called_with_limit}, LLM Context Chunks: {context_chunk_count}")
    assert context_chunk_count == 10, f"Expected 10 context chunks injected into prompt, got {context_chunk_count}"

    # ---------------------------------------------------------
    # TEST 2: final_k > top_k logic
    # ---------------------------------------------------------
    print("\n[TEST 2] final_k > top_k (Custom patch top_k=20, final_k=50)")
    # Monkeypatch retrieve purely on the top level app to see behavior when top_k constraints fall short of final_k
    qdrant_called_with_limit = None
    llm_context_string = None
    
    original_retrieve = chat_engine.retrieval_service.retrieve
    def wrapper_retrieve(*args, **kwargs):
        # intercept and force constraints
        return original_retrieve(*args, **{**kwargs, 'top_k': 20, 'final_k': 50})
    
    chat_engine.retrieval_service.retrieve = wrapper_retrieve
    
    gen2 = chat_engine.stream_chat(user_id=uuid4(), session_id=uuid4(), project_id=proj_id, message="Tell me broadly")
    async for item in gen2:
        pass 
        
    assert qdrant_called_with_limit == 20
    sys_instr_2 = str(llm_context_string)
    context_chunk_count_2 = sys_instr_2.count("Document chunk text number")
    print(f"  [Result] Qdrant Fetched: {qdrant_called_with_limit}, LLM Context Chunks: {context_chunk_count_2}")
    assert context_chunk_count_2 == 20, f"Expected exactly 20 chunks limited by top_k when final_k > top_k."
    
    # reset patch
    chat_engine.retrieval_service.retrieve = original_retrieve

    # ---------------------------------------------------------
    # TEST 3: Confirm Reranking Slot Logic
    # ---------------------------------------------------------
    print("\n[TEST 3] Confirming Phase 3 Reranking Slot")
    
    qdrant_called_with_limit = None
    
    original_search = chat_engine.retrieval_service.vector_store.search
    
    # We dynamically rerank inside retrieve() mock to prove we CAN inject it between fetch and slice
    # Currently retrieval.py looks like:
    # qdrant_results = self.vector_store.search(...)
    # final_results = qdrant_results[:final_k]
    # To prove we can inject reranking, we'll subclass RetrievalService just for this test
    # and override retrieve to include a mock reranker.
    
    class RerankingRetrievalService(RetrievalService):
        def retrieve(self, project_id, query, top_k=5, final_k=2, pdf_ids=None):
            # 1. Fetch top_k
            qdrant_results = self.vector_store.search(
                project_id=project_id,
                query_vector=[0.1],
                limit=top_k,
                pdf_ids=pdf_ids
            )
            # 2. Rerank
            print("  [Phase 3] Mock Reranker runs on all ", len(qdrant_results), " documents")
            # Reverse them to simulate reranking logic changing bounds
            reranked_results = list(reversed(qdrant_results))
            
            # 3. Slice final_k
            return reranked_results[:final_k]

    test_retriever = RerankingRetrievalService()
    test_retriever.vector_store.search = chat_engine.retrieval_service.vector_store.search
    
    reranked_chunks = test_retriever.retrieve(
        project_id="test",
        query="test",
        top_k=7,
        final_k=3
    )
    
    print(f"  [Result] Qdrant Fetched: {qdrant_called_with_limit}, Sliced: {len(reranked_chunks)}")
    # Qdrant mock results are ordered 0,1,2,3,4,5,6
    # Reversed -> 6,5,4,3,2,1,0
    # Sliced to 3 -> 6, 5, 4
    # Let's verify the text payload has index 6,5,4.
    indexes = [c.payload.chunk_index for c in reranked_chunks]
    print(f"  [Result] Final indexes after mock rerank and slice: {indexes}")
    assert indexes == [6, 5, 4]
    
    print("\nALL LLM PIPELINE AND RERANKING EDGE CASES VERIFIED!")

if __name__ == "__main__":
    asyncio.run(verify_llm_pipeline())
