import sys
import os
import json
import asyncio
from unittest.mock import MagicMock, AsyncMock
from collections import namedtuple

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.retrieval import RetrievalService, RERANKER_AVAILABLE

MockPayload = namedtuple('MockPayload', ['project_id', 'pdf_id', 'page_number', 'chunk_index', 'text', 'filename', 'type', 'is_ocr', 'section'])
class MockResult:
    def __init__(self, payload, score):
        self.payload = payload
        self.score = score

def verify_reranking():
    print("--- Verifying Retrieval Phase 3 Reranking Layer ---")
    retrieval_service = RetrievalService()
    
    retrieval_service.embedding_service.generate_embeddings = MagicMock(return_value=[[0.1]*3072])
    
    # We will mock Qdrant to return 5 results.
    # We make Qdrant's ordering mathematically opposite (or different) from what the CrossEncoder will predict.
    # Qdrant Order: [Chunk 0 (High dense), Chunk 1, Chunk 2, Chunk 3, Chunk 4 (Low dense)]
    def mock_qdrant_search(**kwargs):
        results = []
        for i in range(5):
            payload = MockPayload("proj", "pdf", 1, i, f"Document chunk {i}", "file.pdf", "text", False, "")
            results.append(MockResult(payload=payload, score=0.9 - (i*0.1))) # Descending dense scores
        return results
        
    retrieval_service.vector_store.search = MagicMock(side_effect=mock_qdrant_search)

    if RERANKER_AVAILABLE:
        # Mock the CrossEncoder's predict method so we don't have to wait for real NN inference
        # If the input was [0,1,2,3,4], the Mock Qdrant returned them in that exact order (0 is best in dense search).
        # Let's say our Mock Reranker totally flips the relevance: 4 is actually the real best match.
        def mock_predict(pairs):
            print(f"  [CrossEncoder Mock] Scoring {len(pairs)} pairs...")
            return [0.1, 0.2, 0.3, 0.4, 0.99] # Best is the last one (Chunk 4)
            
        import app.services.retrieval as retrieval_module
        retrieval_module.cross_encoder_model.predict = MagicMock(side_effect=mock_predict)
        
        # Test 1: Normal Reranking Execution
        print("\n[TEST 1] Normal Reranking Execution (Ambiguous query)")
        results = retrieval_service.retrieve(
            project_id="test", query="ambiguous query", top_k=5, final_k=3
        )
        
        final_indexes = [r['chunk_index'] for r in results]
        
        print(f"  [Result] Before Rerank: [0, 1, 2, 3, 4] | After Rerank sliced to final_k=3: {final_indexes}")
        assert final_indexes == [4, 3, 2], f"Reranking failed to sort by cross_encoder scores, got {final_indexes}"
        print("  -> Passed! Reranking correctly reordered results overriding dense-search.")
        
        # Test 2: Fallback Logic On Exception
        print("\n[TEST 2] Reranker Failure (Simulating unavailability)")
        
        # Force it to throw an error
        retrieval_module.cross_encoder_model.predict = MagicMock(side_effect=Exception("API limit exceeded / GPU Out of Memory"))
        
        results_fallback = retrieval_service.retrieve(
            project_id="test", query="ambiguous query", top_k=5, final_k=3
        )
        final_indexes_fb = [r['chunk_index'] for r in results_fallback]
        
        print(f"  [Result] Fallback ordered gracefully (should match original dense slices): {final_indexes_fb}")
        assert final_indexes_fb == [0, 1, 2], f"Fallback ordering didn't match original dense-search top_k, got {final_indexes_fb}"
        print("  -> Passed! Fallback served un-reranked valid results upon failure without crashing logic.")
        
    else:
        print("FAIL: Reranker dependency not available in RetrievalService")
        sys.exit(1)
        
    print("\nALL VERIFICATIONS PASSED!")

if __name__ == "__main__":
    verify_reranking()
