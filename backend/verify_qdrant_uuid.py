import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from qdrant_client import QdrantClient
from qdrant_client.http import models

import app.db.qdrant as db_qdrant
memory_client = QdrantClient(":memory:")
db_qdrant.qdrant_client = memory_client

memory_client.create_collection(
    collection_name="document_chunks",
    vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
    on_disk_payload=False
)

from app.services.vector_store import VectorStoreService
from app.services.pdf_parser import PDFParserService

def run_verify():
    vs = VectorStoreService()
    parser = PDFParserService()
    
    pdf_id = "test_doc_deterministic"
    project_id = "test_proj"
    
    def simulate_indexing():
        gen = parser.parse_pdf_generator(pdf_id=pdf_id, project_id=project_id, filename="MYsql notes T.pdf", file_path="../MYsql notes T.pdf")
        batches = []
        for _, chunks in gen:
            for c in chunks:
                batches.append({"payload": c, "vector": [0.1] * 768})
            break # 1 page is enough
        vs.upsert_chunks(batches)
        
    print("--- 1. First Pass Indexing ---")
    simulate_indexing()
    
    # Check count
    count1 = memory_client.count(collection_name=vs.COLLECTION_NAME).count
    print(f"Total points after Phase 1: {count1}")
    
    # Grab the IDs mapped natively
    res1 = memory_client.scroll(collection_name=vs.COLLECTION_NAME, limit=count1)[0]
    ids1 = [p.id for p in res1]
    print(f"Generated Keys Phase 1: {ids1}")
    
    print("\n--- 2. Second Pass Indexing (Re-indexing exact struct) ---")
    simulate_indexing()
    
    # Check count natively mapping constraints without duplicate increments
    count2 = memory_client.count(collection_name=vs.COLLECTION_NAME).count
    print(f"Total points after Phase 2: {count2}")
    
    res2 = memory_client.scroll(collection_name=vs.COLLECTION_NAME, limit=count2)[0]
    ids2 = [p.id for p in res2]
    
    assert count1 == count2, f"Idempotency FAIL! Expected {count1} points, but got {count2}."
    assert set(ids1) == set(ids2), "Keys generated differ organically!"
    
    print("VERIFIED PASS: Point count did not change! Reindexing gracefully overwrote duplicate vectors based on deterministic IDs.")

if __name__ == "__main__":
    run_verify()
