import sys
import os
import json
from unittest.mock import MagicMock
from collections import namedtuple
import math

# Ensure backend path is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.retrieval import RetrievalService
from app.services.evidence_verifier import EvidenceVerifier
import app.services.retrieval as ret_module

MockPayload = namedtuple('MockPayload', ['project_id', 'pdf_id', 'page_number', 'chunk_index', 'text', 'filename', 'type', 'is_ocr', 'section'])
class MockResult:
    def __init__(self, payload, score=None):
        self.payload = payload
        self.score = score

def create_mock_result(text, score=0.9, pdf_id="pdf_1", page=1):
    payload = MockPayload("proj_1", pdf_id, page, 1, text, f"{pdf_id}.pdf", "text", False, "body")
    return MockResult(payload, score)

def run_tests():
    print("--- Retrieval & Grounding Test Suite ---")
    
    ret_service = RetrievalService()
    ev_verifier = EvidenceVerifier()

    # Mocks
    ret_service.embedding_service.generate_embeddings = MagicMock(return_value=[[0.1]*768])
    ev_verifier.embedding_service.generate_embeddings = MagicMock(side_effect=lambda texts: [[0.5]*768 for _ in texts])

    # 1. Relevant query returns expected chunks
    print("\n1. Testing relevant query...")
    def mock_search_relevant(**kwargs):
        return [create_mock_result("This is a highly relevant chunk about databases.", 0.9)]
    ret_service.vector_store.search = MagicMock(side_effect=mock_search_relevant)
    results = ret_service.retrieve("proj_1", "databases")
    assert len(results) > 0
    assert "databases" in results[0]['text']
    print("PASS: Relevant query")

    # 2. Irrelevant query returns low-relevance/empty results appropriately
    print("\n2. Testing irrelevant query...")
    def mock_search_irrelevant(**kwargs):
        # Qdrant would return zero matches due to thresholding or limits 
        return []
    ret_service.vector_store.search = MagicMock(side_effect=mock_search_irrelevant)
    results = ret_service.retrieve("proj_1", "apples")
    assert len(results) == 0
    print("PASS: Irrelevant query")

    # 3. Exact-keyword/identifier query (validates 3.3 hybrid path)
    print("\n3. Testing exact-keyword query (hybrid simulation)...")
    def mock_search_exact(**kwargs):
        # Simulate returning a high-score BM25/Exact match
        return [create_mock_result("ID: ABC-123. System configuration is stable.", 0.99)]
    ret_service.vector_store.search = MagicMock(side_effect=mock_search_exact)
    results = ret_service.retrieve("proj_1", "ABC-123")
    assert "ABC-123" in results[0]["text"]
    print("PASS: Exact-keyword/hybrid simulation")

    # 4. Multi-document query returns evidence from multiple sources
    print("\n4. Testing multi-document query...")
    def mock_search_multi(**kwargs):
        return [
            create_mock_result("Doc A context here.", pdf_id="doc_A"),
            create_mock_result("Doc B context here.", pdf_id="doc_B")
        ]
    ret_service.vector_store.search = MagicMock(side_effect=mock_search_multi)
    results = ret_service.retrieve("proj_1", "compare A and B")
    pdf_ids = {r["pdf_id"] for r in results}
    assert len(pdf_ids) == 2
    assert "doc_A" in pdf_ids and "doc_B" in pdf_ids
    print("PASS: Multi-document evidence")

    # 5. top_k/final_k contract behaves as configured (3.1)
    print("\n5. Testing top_k/final_k contract...")
    def mock_search_contract(**kwargs):
        return [create_mock_result(f"Chunk {i}", 0.8) for i in range(20)]
    ret_service.vector_store.search = MagicMock(side_effect=mock_search_contract)
    results = ret_service.retrieve("proj_1", "test context", top_k=20, final_k=5)
    assert len(results) == 5
    print("PASS: top_k/final_k contract maintained")

    # 6. Reranking improves ordering on a known test case (3.2)
    print("\n6. Testing reranking structure ordering...")
    old_avail = ret_module.RERANKER_AVAILABLE
    old_model = ret_module.cross_encoder_model
    
    ret_module.RERANKER_AVAILABLE = True
    class MockReranker:
        def predict(self, pairs):
            # Reverse original mock order: if standard yields 0 then 1
            # Reranker predicts 1.0 (for index 0), 2.0 (for index 1)
            # Higher score will move it to front.
            return [float(i + 1) for i in range(len(pairs))]
    ret_module.cross_encoder_model = MockReranker()
    
    def mock_search_rerank(**kwargs):
        return [
            create_mock_result("Initially first", 0.9), 
            create_mock_result("Initially second (but better context)", 0.8)
        ]
    ret_service.vector_store.search = MagicMock(side_effect=mock_search_rerank)
    results = ret_service.retrieve("proj_1", "test query")
    assert len(results) == 2
    # The second item scored higher (2.0) by MockReranker, so it should be placed first
    assert "Initially second" in results[0]["text"]
    
    # Restore modules
    ret_module.RERANKER_AVAILABLE = old_avail
    ret_module.cross_encoder_model = old_model
    print("PASS: Reranking structure operative properly prioritizes scores")

    # 7. Grounded-answer supported-claim case
    print("\n7. Testing grounded answer (supported claim)...")
    claim_text = "The system configuration is stable."
    chunks = [create_mock_result("System configuration is completely stable.", 0.9).payload._asdict()]
    ev_verifier.cosine_similarity = MagicMock(return_value=0.8) # > 0.65 threshold
    verified = ev_verifier.verify_claims(claim_text, chunks)
    assert verified[0]["supported"] is True
    print("PASS: Supported claim case logic")

    # 8. Unsupported-question case (model states insufficient evidence)
    print("\n8. Testing unsupported claim (insufficient evidence)...")
    claim_text = "The system uses alien technology."
    chunks = [create_mock_result("System configuration is completely stable.", 0.9).payload._asdict()]
    ev_verifier.cosine_similarity = MagicMock(return_value=0.2) # < 0.65 threshold
    verified = ev_verifier.verify_claims(claim_text, chunks)
    assert verified[0]["supported"] is False
    print("PASS: Unsupported claim case caught")

    # 9. Citation accuracy against known ground-truth chunks
    print("\n9. Testing citation mapping accuracy...")
    claim_text = "The system uses XML parsing natively."
    chunk_pld = create_mock_result("The system uses XML parsing natively.", pdf_id="doc_xml", page=12).payload._asdict()
    ev_verifier.cosine_similarity = MagicMock(return_value=0.95)
    verified = ev_verifier.verify_claims(claim_text, [chunk_pld])
    assert verified[0]["pdf_id"] == "doc_xml"
    assert verified[0]["page"] == 12
    assert verified[0]["filename"] == "doc_xml.pdf"
    print("PASS: Citation accuracy mapped")

    # 10. Adversarial hallucination check (Phase 4 Logic)
    print("\n10. Testing adversarial hallucination interception (Phase 4)...")
    adv_claim = "As an AI, I confirm aliens built this software in 1999."
    corpus = [create_mock_result("The project was built by contributors in 2021.").payload._asdict()]
    ev_verifier.cosine_similarity = MagicMock(return_value=0.1) # extremely weak support
    results = ev_verifier.verify_claims(adv_claim, corpus)
    assert not results[0]["supported"]
    assert results[0]["confidence"] == 0.1
    print("PASS: Adversarial hallucination intercepted")

    print("\nALL VERIFICATIONS PASSED")

if __name__ == "__main__":
    run_tests()
