import sys
import os
import json
from qdrant_client import QdrantClient
from qdrant_client.http import models

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Monkey patch Qdrant Singleton before importing VectorStoreService
import app.db.qdrant as db_qdrant
memory_client = QdrantClient(":memory:")
db_qdrant.qdrant_client = memory_client

memory_client.create_collection(
    collection_name="document_chunks",
    vectors_config=models.VectorParams(
        size=768, # using 768 for test vectors to avoid text-embedding costs
        distance=models.Distance.COSINE
    ),
    on_disk_payload=False
)

from app.services.vector_store import VectorStoreService, ChunkPayload
from app.services.retrieval import RetrievalService
from app.services.pdf_parser import PDFParserService

def run_verification():
    vs = VectorStoreService()
    
    # 1. Provide an Existing/Legacy Points in Qdrant (Simulating the state of already indexed data)
    memory_client.upsert(
        collection_name=vs.COLLECTION_NAME,
        points=[
            models.PointStruct(
                id="c2a9a973-4f96-48be-8bc9-9304a441e8c9",
                vector=[0.1] * 768,
                payload={
                    "project_id": "legacy_proj",
                    "pdf_id": "legacy_pdf",
                    "page_number": 1,
                    "chunk_index": 0,
                    "text": "This is legacy content extracted previously.",
                    "filename": "old_doc.pdf"
                }
            )
        ]
    )
    print("--- 1. Inserted Legacy Point (No reindexing required) ---")
    
    # 2. Use real pipeline nodes to generate and index NEW payload
    parser = PDFParserService()
    gen = parser.parse_pdf_generator(pdf_id="new_pdf_456", project_id="proj_xyz", filename="MYsql notes T.pdf", file_path="../MYsql notes T.pdf")
    
    batches = []
    for data, chunks in gen:
        for c in chunks:
            c["vector"] = [0.2] * 768
            batches.append({"payload": c, "vector": [0.2] * 768})
        break # fetch first page only
        
    vs.upsert_chunks(batches)
    print("\n--- 2. New Document Indexed using Native Write Path ---")
    
    # 3. Inspect the RAW payload actually stored in Qdrant for new points (bypass Pydantic)
    raw_results, _ = memory_client.scroll(
        collection_name=vs.COLLECTION_NAME,
        scroll_filter=models.Filter(
            must=[models.FieldCondition(key="pdf_id", match=models.MatchValue(value="new_pdf_456"))]
        ),
        limit=1
    )
    
    print("\n--- 3. RAW Payload from Qdrant (New Document) ---")
    raw_payload = raw_results[0].payload
    print(json.dumps(raw_payload, indent=2))
    
    expected_keys = {"project_id", "pdf_id", "page_number", "chunk_index", "text", "filename", "type", "is_ocr", "section"}
    actual_keys = set(raw_payload.keys())
    assert expected_keys == actual_keys, f"Schema mismatch! Keys present: {actual_keys}"
    print(f"VERIFIED: All exact required fields are present in the RAW dictionary! type={raw_payload['type']}")
    
    print("\n--- 4. Run Retrieval on New Document ---")
    retrieval = RetrievalService()
    retrieval.vector_store.client = memory_client  # Ensure client is physically present
    # Mock embedder to avoid LLM API network costs in this test script
    retrieval.embedding_service.generate_embeddings = lambda textes: [[0.2] * 768] * len(textes)
    
    out_new = retrieval.retrieve(project_id="proj_xyz", query="test query", final_k=1, pdf_ids=["new_pdf_456"])
    print("New Document Retrieval Keys:", list(out_new[0].keys()))
    assert "type" in out_new[0] and out_new[0]["type"] == "chunk", "Type missing in new retrieval!"
    print("PASS: Retrieved successfully without errors on NEW schema.")
    
    print("\n--- 5. Run Retrieval on Legacy Collection ---")
    out_legacy = retrieval.retrieve(project_id="legacy_proj", query="test", final_k=1, pdf_ids=["legacy_pdf"])
    print("Legacy Document Retrieval Keys:", list(out_legacy[0].keys()))
    assert "type" in out_legacy[0] and out_legacy[0]["type"] == "chunk", "Pydantic fallback failed for legacy type!"
    print(f"Legacy payload 'type': {out_legacy[0]['type']} (Defaulted successfully via Pydantic backwards compatibility)")
    print("PASS: Retrieved successfully against legacy vector schema without runtime errors.")

if __name__ == "__main__":
    run_verification()
