import sys
import os
import uuid
import logging
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.retrieval import RetrievalService
from app.services.vector_store import VectorStoreService, ChunkPayload, SearchResult
from qdrant_client.http import models

logging.basicConfig(level=logging.ERROR)

def run_verification():
    project_id = str(uuid.uuid4())
    doc1_id = str(uuid.uuid4())
    doc2_id = str(uuid.uuid4())
    
    retrieval = RetrievalService()
    vs = VectorStoreService()
    
    # Mocking the Qdrant Client to intercept search filters instead of actual network execution
    mock_client = MagicMock()
    retrieval.vector_store.client = mock_client
    
    query = "fruit"
    
    # 1. Unscoped query
    print("\n[1] Testing UNSCOPED query (no pdf_ids)...")
    try:
        retrieval.retrieve(project_id, query, top_k=50, final_k=10)
    except Exception as e:
        pass # Allow fail after our assertions
        
    # Find the filter passed to query_points
    unscoped_call = mock_client.query_points.call_args
    assert unscoped_call is not None, "query_points was not called"
    query_filter = unscoped_call.kwargs.get("query_filter")
    
    must_keys = [cond.key for cond in query_filter.must]
    print(f"    Filter keys applied: {must_keys}")
    assert "project_id" in must_keys
    assert "pdf_id" not in must_keys, "Unscoped search should not restrict pdf_id!"
    print("    [PASS] Unscoped search behaves correctly.")


    # 2. Scoped query
    print("\n[2] Testing SCOPED query (pdf_ids=[doc1_id])...")
    try:
        retrieval.retrieve(project_id, query, top_k=50, final_k=10, pdf_ids=[doc1_id])
    except Exception as e:
        pass # Allow fail after our assertions
        
    scoped_call = mock_client.query_points.call_args
    query_filter = scoped_call.kwargs.get("query_filter")
    
    must_keys = [cond.key for cond in query_filter.must]
    print(f"    Filter keys applied: {must_keys}")
    assert "project_id" in must_keys
    assert "pdf_id" in must_keys, "Scoped search must restrict pdf_id!"
    
    # Inspect the match condition for pdf_id
    pdf_condition = next((c for c in query_filter.must if c.key == "pdf_id"), None)
    
    # Ensure it's using MatchAny
    assert isinstance(pdf_condition.match, models.MatchAny), "Should use MatchAny for pdf filter!"
    assert pdf_condition.match.any == [doc1_id], "Should restrict exactly to the provided document ID"
    
    print("    [PASS] Scoped search securely bounds queries targeting only specific Document UUIDs.")
    
    print("\n✅ All Document-Scoped Query Constraints Behavior mathematically evaluated and verified successfully!")

if __name__ == "__main__":
    run_verification()
