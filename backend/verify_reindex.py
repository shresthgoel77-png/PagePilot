import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from qdrant_client import QdrantClient
from qdrant_client.http import models

# Mocking database to memory mapping exactly mirroring the Qdrant local setup
import app.db.qdrant as db_qdrant
memory_client = QdrantClient(":memory:")
db_qdrant.qdrant_client = memory_client

memory_client.create_collection(
    collection_name="document_chunks",
    vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
    on_disk_payload=False
)

from app.services.vector_store import VectorStoreService, ChunkPayload
from app.services.admin_reindex import AdminReindexService

def run_verify():
    vs = VectorStoreService()
    admin = AdminReindexService()
    
    # Let's bypass raw embedding API network limits internally avoiding actual calls.
    admin.embeddings.generate_embeddings = lambda texts: [[0.1] * 768] * len(texts)
    
    pdf_id = "reindex_pdf_321"
    project_id = "test_proj"
    
    # 1. We mock a PDF Parser outputting exactly 3 chunks statically.
    def mock_parser_3_chunks(*args, **kwargs):
        chunks = [
            {"project_id": project_id, "pdf_id": pdf_id, "page_number": 1, "chunk_index": 0, "text": "C1", "filename": "test", "type": "chunk", "is_ocr": False, "section": None},
            {"project_id": project_id, "pdf_id": pdf_id, "page_number": 1, "chunk_index": 1, "text": "C2", "filename": "test", "type": "chunk", "is_ocr": False, "section": None},
            {"project_id": project_id, "pdf_id": pdf_id, "page_number": 1, "chunk_index": 2, "text": "C3", "filename": "test", "type": "chunk", "is_ocr": False, "section": None}
        ]
        yield None, chunks
        
    admin.parser.parse_pdf_generator = mock_parser_3_chunks
    
    print("--- 1. Initial Indexing Sequence (Creating 3 Chunks) ---")
    metrics_1 = admin.reindex_pdf(pdf_id, project_id, "test.pdf", "../test", dry_run=False)
    count_1 = memory_client.count(collection_name=vs.COLLECTION_NAME).count
    print(f"Metrics 1: {metrics_1}")
    print(f"Total points mathematically: {count_1}")
    assert count_1 == 3, "Failed to insert initial batch completely."
    
    print("\n--- 2. Simulating Chunking Logic Change (Now generating only 2 chunks) ---")
    def mock_parser_2_chunks(*args, **kwargs):
        chunks = [
            {"project_id": project_id, "pdf_id": pdf_id, "page_number": 1, "chunk_index": 0, "text": "C1_new", "filename": "test", "type": "chunk", "is_ocr": False, "section": None},
            {"project_id": project_id, "pdf_id": pdf_id, "page_number": 1, "chunk_index": 1, "text": "C2_new", "filename": "test", "type": "chunk", "is_ocr": False, "section": None}
        ]
        yield None, chunks
        
    admin.parser.parse_pdf_generator = mock_parser_2_chunks
    
    # 3. Perform a DRY RUN
    print("\n--- 3. DRY RUN Reindexing ---")
    metrics_dry = admin.reindex_pdf(pdf_id, project_id, "test.pdf", "../test", dry_run=True)
    count_dry = memory_client.count(collection_name=vs.COLLECTION_NAME).count
    print(f"Metrics Dry Run: {metrics_dry}")
    print(f"Total points post-dry-run natively: {count_dry}")
    
    assert metrics_dry["updates"] == 2, "Expected 2 existing chunks to be updated matching exact indices."
    assert metrics_dry["adds"] == 0, "Expected 0 inserts natively."
    assert metrics_dry["removes"] == 1, "Expected exactly 1 orphan mathematically mapped (chunk_index=2) remaining natively!"
    assert count_dry == 3, "Dry run mutated the database destructively! Action failed securely."
    
    # 4. Perform a LIVE LIVE RUN
    print("\n--- 4. EXECUTING LIVE Reindex Sequence ---")
    metrics_live = admin.reindex_pdf(pdf_id, project_id, "test.pdf", "../test", dry_run=False)
    count_live = memory_client.count(collection_name=vs.COLLECTION_NAME).count
    print(f"Metrics LIVE: {metrics_live}")
    print(f"Total points mapped perfectly natively: {count_live}")
    
    assert count_live == 2, "Orphan block deletion missed targeting structurally! Database remained polluted natively."
    
    # Verify explicitly what was saved iteratively
    res = memory_client.scroll(collection_name=vs.COLLECTION_NAME, limit=10)[0]
    payloads = [p.payload["text"] for p in res]
    print(f"Successfully remaining texts: {payloads}")
    assert set(payloads) == {"C1_new", "C2_new"}, f"Invalid payloads preserved iteratively: {payloads}"
    
    print("VERIFIED PASS: Admin Reindex executed mathematical overwrites mapping explicit orphans securely tracking identically mapped bounds without global destructing sweep!")

if __name__ == "__main__":
    run_verify()
