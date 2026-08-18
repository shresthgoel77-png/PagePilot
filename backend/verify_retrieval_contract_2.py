import sys
import os
import json
from unittest.mock import MagicMock
from collections import namedtuple

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.retrieval import RetrievalService

def verify_retrieval_contract():
    print("--- Verifying Retrieval top_k vs final_k Contract ---")
    
    retrieval_service = RetrievalService()
    
    # Mock embedding
    retrieval_service.embedding_service.generate_embeddings = MagicMock(return_value=[[0.1] * 3072])
    
    # Create namedtuple for mock Qdrant payload
    MockPayload = namedtuple('MockPayload', ['project_id', 'pdf_id', 'page_number', 'chunk_index', 'text', 'filename', 'type', 'is_ocr', 'section'])
    MockResult = namedtuple('MockResult', ['payload', 'score'])
    
    # We will track what `limit` Qdrant was called with
    qdrant_called_with_limit = None
    
    def mock_search(**kwargs):
        nonlocal qdrant_called_with_limit
        qdrant_called_with_limit = kwargs.get('limit')
        print(f"DEBUG: vector_store.search called with limit={qdrant_called_with_limit}")
        
        # Return exact number of dummy records requested by limit
        results = []
        for i in range(qdrant_called_with_limit or 0):
            payload = MockPayload("proj", "pdf", 1, i, f"text_{i}", "file.pdf", "text", False, "")
            results.append(MockResult(payload=payload, score=0.9))
        return results

    retrieval_service.vector_store.search = MagicMock(side_effect=mock_search)

    # Test Case 1: Fetch 50, return 5
    top_k_test = 50
    final_k_test = 5
    print("\nExecuting retrieve() with top_k=50, final_k=5...")
    results = retrieval_service.retrieve(
        project_id="test_proj",
        query="test query",
        top_k=top_k_test,
        final_k=final_k_test
    )
    print(f"Results returned to LLM context: {len(results)}")
    
    assert qdrant_called_with_limit == top_k_test, f"Qdrant fetched {qdrant_called_with_limit}, expected {top_k_test}"
    assert len(results) == final_k_test, f"Context received {len(results)}, expected {final_k_test}"
    
    # Test Case 2: Insufficient candidates in VectorStore
    # We forcefully limit VectorStore to return only 3 items, even if top_k=50
    def mock_search_limited(**kwargs):
        nonlocal qdrant_called_with_limit
        qdrant_called_with_limit = kwargs.get('limit')
        print(f"DEBUG: vector_store.search (limited mock) called with limit={qdrant_called_with_limit}")
        
        results = []
        for i in range(3): # Only 3 exist!
            payload = MockPayload("proj", "pdf", 1, i, f"text_{i}", "file.pdf", "text", False, "")
            results.append(MockResult(payload=payload, score=0.9))
        return results
        
    retrieval_service.vector_store.search = MagicMock(side_effect=mock_search_limited)

    print("\nExecuting retrieve() where VectorStore only has 3 items, final_k=10...")
    results_2 = retrieval_service.retrieve(
        project_id="test_proj",
        query="test query",
        top_k=50,
        final_k=10
    )
    print(f"Results returned to LLM context: {len(results_2)}")
    assert len(results_2) == 3, f"Context received {len(results_2)}, expected 3"
    
    print("\nALL VERIFICATIONS PASSED: The top_k and final_k contract logic flows correctly.")
    
if __name__ == "__main__":
    verify_retrieval_contract()
