import sys
import os
from collections import namedtuple

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.retrieval import RetrievalService, cross_encoder_model

MockPayload = namedtuple('MockPayload', ['project_id', 'pdf_id', 'page_number', 'chunk_index', 'text', 'filename', 'type', 'is_ocr', 'section'])
class MockResult:
    def __init__(self, payload, score):
        self.payload = payload
        self.score = score

def verify_real_cross_encoder():
    print("--- Verifying Real Cross-Encoder Reranking ---")
    retrieval_service = RetrievalService()
    
    # We will formulate an ambiguous query where simple keyword overlap might favor a wrong document
    query = "How to handle database scaling?"
    
    # Fake Qdrant results returning in suboptimal order (e.g. maybe dense vectors liked chunk 0 more because of similar words)
    mock_qdrant_results = [
        # Suboptimal, but ranked 1st by dense search (pretend)
        MockResult(
            payload=MockPayload("proj", "pdf", 1, 0, "Scaling a fish involves removing scales before cooking. You can use a knife to handle the scaling process.", "fish.pdf", "text", False, ""),
            score=0.9
        ),
        # Somewhat relevant, ranked 2nd
        MockResult(
            payload=MockPayload("proj", "pdf", 1, 1, "To handle the situation, we need to scale our team up.", "team.pdf", "text", False, ""),
            score=0.85
        ),
        # Highly relevant, but ranked 3rd by dense search
        MockResult(
            payload=MockPayload("proj", "pdf", 1, 2, "Database scaling can be achieved through sharding or replication to handle increased load.", "db.pdf", "text", False, ""),
            score=0.8
        )
    ]
    
    # We mock only the vector_store.search so it returns these fake results.
    # We let the REAL cross_encoder_model run!
    def mock_search(**kwargs):
        import copy
        return copy.deepcopy(mock_qdrant_results)
        
    retrieval_service.vector_store.search = mock_search
    retrieval_service.embedding_service.generate_embeddings = lambda x: [[0.1]*3072]
    
    # -------------------------------------------------------------
    # 1. TEST REAL CROSS-ENCODER
    # -------------------------------------------------------------
    print(f"\nQuery: '{query}'")
    print("\n[Dense Search Original Order (top_k=3)]:")
    for i, res in enumerate(mock_qdrant_results):
        print(f"  {i}) Index {res.payload.chunk_index}: '{res.payload.text}'")
        
    print("\nExecuting retrieve() with real reranker enabled...")
    final_results = retrieval_service.retrieve(project_id="t", query=query, top_k=3, final_k=3)
    
    print("\n[Reranker Final Order (final_k=3)]:")
    for i, res in enumerate(final_results):
         # remember retrieve maps to dicts
        print(f"  {i}) Index {res['chunk_index']}: '{res['text']}' (New score: {res.get('score', 'N/A')})")
        
    # Validation: the DB scaling text (Index 2) should be Rank 0 now!
    final_indexes = [r['chunk_index'] for r in final_results]
    assert final_indexes[0] == 2, f"Failed: Highly relevant chunk wasn't ranked first. Order was {final_indexes}"
    
    # -------------------------------------------------------------
    # 2. TEST FAILURE PATH
    # -------------------------------------------------------------
    import app.services.retrieval as ret_mod
    original_predict = ret_mod.cross_encoder_model.predict
    
    def fake_crash(pairs):
        raise Exception("Simulated GPU Out of Memory Error inside CrossEncoder")
        
    ret_mod.cross_encoder_model.predict = fake_crash
    
    print("\nExecuting retrieve() with simulated CrossEncoder crash...")
    fallback_results = retrieval_service.retrieve(project_id="t", query=query, top_k=3, final_k=3)
    
    print("\n[Fallback Order (final_k=3)]:")
    for i, res in enumerate(fallback_results):
        print(f"  {i}) Index {res['chunk_index']}: '{res['text']}'")
        
    fallback_indexes = [r['chunk_index'] for r in fallback_results]
    assert fallback_indexes == [0, 1, 2], f"Failed: Fallback order didn't match original dense order [0,1,2]. Got {fallback_indexes}"
    
    # Restore predict
    ret_mod.cross_encoder_model.predict = original_predict
    
    print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    verify_real_cross_encoder()
