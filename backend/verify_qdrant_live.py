import sys
import os
import json
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.qdrant import qdrant_client
from app.services.vector_store import VectorStoreService, ChunkPayload
from app.services.pdf_parser import PDFParserService
from app.services.embeddings import EmbeddingService
from qdrant_client.http import models

def verify_live():
    # Make sure Qdrant is up
    if not qdrant_client:
        print("FAIL: Live Qdrant Client Not Connected!")
        sys.exit(1)
        
    vs = VectorStoreService()
    parser = PDFParserService()
    embeddings = EmbeddingService()
    
    # Mock embedder to save time and API calls
    embeddings.generate_embeddings = lambda texts: [[0.1] * 3072] * len(texts)
    
    pdf_id = "real_pdf_test_99"
    project_id = "test_project"
    
    # We clear the specific test doc before starting, just to have a clean slate for the test
    vs.delete_by_pdf(pdf_id)
    
    def simulate_app_indexing_path():
        gen = parser.parse_pdf_generator(pdf_id, project_id, "MYsql notes T.pdf", "../MYsql notes T.pdf")
        
        # 1. Parsing
        all_chunks = []
        for _, chunks in gen:
            all_chunks.extend(chunks)
            
        # 2. Embedding + Structuring
        vecs = embeddings.generate_embeddings([c["text"] for c in all_chunks])
        batches = [{"payload": c, "vector": v} for c, v in zip(all_chunks, vecs)]
        
        # 3. Indexing
        vs.upsert_chunks(batches)
    
    def fetch_all_ids():
        res = vs.client.scroll(
            collection_name=vs.COLLECTION_NAME,
            scroll_filter=models.Filter(must=[models.FieldCondition(key="pdf_id", match=models.MatchValue(value=pdf_id))]),
            limit=100
        )
        return [p.id for p in res[0]]
        
    print("--- FIRST RUN ---")
    simulate_app_indexing_path()
    ids_1 = fetch_all_ids()
    count_1 = len(ids_1)
    
    print("--- SECOND RUN ---")
    simulate_app_indexing_path()
    ids_2 = fetch_all_ids()
    count_2 = len(ids_2)
    
    print(f"Run 1 IDs:\n{ids_1}")
    print(f"Run 2 IDs:\n{ids_2}")
    
    ids_identical = "YES" if set(ids_1) == set(ids_2) and count_1 == count_2 else "NO"
    duplicate_points = "NO" if count_1 == count_2 else "YES"
    
    print(f"IDs identical: {ids_identical}")
    print(f"Point count before/after: {count_1} / {count_2}")
    print(f"Duplicate points: {duplicate_points}")
    print(f"Deterministic seed/formula: uuid.uuid5(uuid.NAMESPACE_DNS, f'{{project_id}}_{{pdf_id}}_{{chunk_index}}')")
    
    if count_1 == count_2 and ids_identical == "YES":
        print("PASS")
    else:
        print("FAIL")

if __name__ == "__main__":
    verify_live()
