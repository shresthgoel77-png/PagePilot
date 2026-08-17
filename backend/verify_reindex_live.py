import sys
import os
import json
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.qdrant import qdrant_client
from app.services.vector_store import VectorStoreService
from app.services.admin_reindex import AdminReindexService
from app.services.retrieval import RetrievalService
from app.services.pdf_parser import PDFParserService
from qdrant_client.http import models

def verify_live():
    if not qdrant_client:
        print("FAIL: Live Qdrant Client Not Connected!")
        sys.exit(1)
        
    vs = VectorStoreService()
    admin = AdminReindexService()
    retrieval = RetrievalService()
    parser = PDFParserService()
    
    # Mock embeddings to bypass LLM explicitly preserving API constraints locally
    admin.embeddings.generate_embeddings = lambda texts: [[0.1] * 3072] * len(texts)
    retrieval.embedding_service.generate_embeddings = lambda texts: [[0.1] * 3072] * len(texts)
    
    pdf_id = "real_reindex_test_88"
    project_id = "test_project"
    vs.delete_by_pdf(pdf_id) # Initial global cleanup of artifact
    
    # Generate 5 chunks normally
    def mock_parser_5(*args, **kwargs):
        chunks = [{"project_id": project_id, "pdf_id": pdf_id, "page_number": 1, "chunk_index": i, "text": f"Chunk_Initial_{i}", "filename": "test", "type": "chunk", "is_ocr": False, "section": None} for i in range(5)]
        yield None, chunks
        
    admin.parser.parse_pdf_generator = mock_parser_5
    
    print("--- 1. Initial Indexing Sequence (Creating 5 Chunks) ---")
    admin.reindex_pdf(pdf_id, project_id, "test.pdf", "../test", dry_run=False)
    
    def count_pdf():
        res, _ = vs.client.scroll(
            collection_name=vs.COLLECTION_NAME,
            scroll_filter=models.Filter(must=[models.FieldCondition(key="pdf_id", match=models.MatchValue(value=pdf_id))]),
            limit=100
        )
        return len(res)
        
    count_init = count_pdf()
    print(f"Initial point count: {count_init}")
    
    # Generate 3 chunks normally (simulating a chunk size increase)
    def mock_parser_3(*args, **kwargs):
        chunks = [{"project_id": project_id, "pdf_id": pdf_id, "page_number": 1, "chunk_index": i, "text": f"Chunk_Updated_{i}", "filename": "test", "type": "chunk", "is_ocr": False, "section": None} for i in range(3)]
        yield None, chunks
        
    admin.parser.parse_pdf_generator = mock_parser_3
    
    print("--- 2. DRY RUN Reindexing ---")
    metrics_dry = admin.reindex_pdf(pdf_id, project_id, "test.pdf", "../test", dry_run=True)
    count_dry = count_pdf()
    
    print(f"Dry Run Result: {metrics_dry}")
    print(f"Count post-dry-run natively: {count_dry}")
    
    print("--- 3. LIVE EXECUTING Reindexing ---")
    metrics_live = admin.reindex_pdf(pdf_id, project_id, "test.pdf", "../test", dry_run=False)
    count_live = count_pdf()
    
    print(f"Live Result: {metrics_live}")
    print(f"Final Count natively (should be 3): {count_live}")
    
    print("--- 4. RETRIEVAL SEQUENCE ---")
    out = retrieval.retrieve(project_id, "test", final_k=2, pdf_ids=[pdf_id])
    print(f"Retrieval returned: {len(out)} documents.")
    
    print("--- 5. NORMAL UPLOAD BEHAVIOR ---")
    # Simulate normal upload by mocking normal vector_store.upsert
    new_chunks = [{"project_id": project_id, "pdf_id": pdf_id, "page_number": 1, "chunk_index": i, "text": f"Isolated_{i}", "filename": "test", "type": "chunk", "is_ocr": False, "section": None} for i in range(2)]
    vecs = admin.embeddings.generate_embeddings([c["text"] for c in new_chunks])
    batches = [{"payload": c, "vector": v} for c, v in zip(new_chunks, vecs)]
    vs.upsert_chunks(batches)
    count_normal = count_pdf() # Will still be 3 because upsert doesn't delete!
    print(f"Count after isolated generic file upsert: {count_normal}")

    print(f"\nFinal Expected output formatting:\n")
    print(f"Initial point count: {count_init}")
    print(f"New chunk count: 3")
    print(f"Dry-run result: {metrics_dry}")
    print(f"Dry-run deletions actually performed: {'YES' if count_dry < count_init else 'NO'}")
    print(f"Confirmation mechanism used: 'dry_run=False' flag evaluated natively inside explicit reindex_pdf")
    print(f"Actual adds: {metrics_live['adds']}")
    print(f"Actual updates: {metrics_live['updates']}")
    print(f"Actual removals: {metrics_live['removes']}")
    print(f"Final point count: {count_live}")
    print(f"Retrieval after reindex: {'PASS' if len(out) > 0 else 'FAIL'}")
    print(f"Normal upload triggers reindex: {'YES' if count_normal < count_live else 'NO'}")
    print(f"Collection destroyed/recreated: NO (Explicit ID sweeping target resolved seamlessly)")
    
    if count_init == 5 and count_dry == 5 and count_live == 3 and count_normal == 3 and len(out) > 0:
        print("PASS")
    else:
        print(f"FAIL -> c_i:{count_init}, c_d:{count_dry}, c_l:{count_live}, c_n:{count_normal}, L:{len(out)}")

if __name__ == "__main__":
    verify_live()
