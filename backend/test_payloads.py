import sys
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.services.retrieval import RetrievalService
from app.services.vector_store import VectorStoreService, ChunkPayload
from qdrant_client.http import models

async def verify_qdrant():
    pdf_path = "../MYsql notes T.pdf"
    
    # 1. Manually insert an "Old Legacy" chunk directly into Qdrant using raw client
    vs = VectorStoreService()
    print("--- Testing Legacy Read ---")
    vs.client.upsert(
        collection_name=vs.COLLECTION_NAME,
        points=[
            models.PointStruct(
                id="c2a9a973-4f96-48be-8bc9-9304a441e8c9",
                vector=[0.1]*3072, # assuming 3072 dims
                payload={
                    "project_id": "legacy_proj",
                    "pdf_id": "legacy_pdf",
                    "page_number": 1,
                    "chunk_index": 0,
                    "text": "This is a legacy text.",
                    "filename": "legacy.pdf"
                    # Missing type, is_ocr, section
                }
            )
        ]
    )
    
    # Retrieve it
    retrieval = RetrievalService()
    # we mock the generic search to bypass embedding just to test payload parsing 
    results = vs.client.search(
        collection_name=vs.COLLECTION_NAME,
        query_vector=[0.1]*3072,
        query_filter=models.Filter(
            must=[models.FieldCondition(key="pdf_id", match=models.MatchValue(value="legacy_pdf"))]
        ),
        limit=1
    )
    if results:
        # Pydantic parsing test
        print("Legacy Pydantic parsing test:", ChunkPayload(**results[0].payload).model_dump())
    
    # 2. Test actual ingestion pipeline
    print("\n--- Testing New Ingestion Pipeline ---")
    # mock a small pdf doc obj
    class MockDoc:
        id = "test_doc_new_5"
        filename = "MYsql notes T.pdf"
        project_id = "test_proj"
        file_path = pdf_path
        status = "processing"
    
    from sqlalchemy.orm import Session
    # Since we can't easily mock DB session if it requires it, we can just call the pdf_parser generator ourselves 
    # instead of the entire pipeline, because the pipeline writes to DB which might cause DB session errors if mocked wrong.
    # Actually, we can just call pdf_parser + vs.upsert directly!
    
    from app.services.pdf_parser import PDFParserService
    parser = PDFParserService()
    gen = parser.parse_pdf_generator(MockDoc.id, MockDoc.project_id, MockDoc.filename, MockDoc.file_path)
    
    batches = []
    # get 1 page only
    for data, chunks in gen:
        for c in chunks:
            # mock vector
            c["vector"] = [0.1]*3072
            # The structure from pdf_parser is stored directly in payload by vs.upsert_chunks(batches)
            batches.append({"payload": c, "vector": [0.1]*3072})
        break
        
    vs.upsert_chunks(batches)
    print("New chunks upserted successfully.")
    
    res_new = vs.client.search(
        collection_name=vs.COLLECTION_NAME,
        query_vector=[0.1]*3072,
        query_filter=models.Filter(
            must=[models.FieldCondition(key="pdf_id", match=models.MatchValue(value="test_doc_new_5"))]
        ),
        limit=1
    )
    
    if res_new:
        print("New Pydantic parsing test:", ChunkPayload(**res_new[0].payload).model_dump())
        
        # Test retrieval layer output unpacking
        # the retrieve method calls embedder which would overwrite our fake vectors, 
        # so let's mock the embedder inside retrieval service
        retrieval.embedding_service.generate_embeddings = lambda text: [[0.1]*3072]
        
        out = retrieval.retrieve(project_id="test_proj", query="test", final_k=1, pdf_ids=["test_doc_new_5"])
        print("\nRetrieval Layer Output Dictionary Keys:", list(out[0].keys()))
        print("Retrieval Layer Output Dictionary:")
        for k,v in out[0].items():
            val = str(v)
            if len(val) > 40: val = val[:40] + "..."
            print(f"  {k}: {val}")

if __name__ == "__main__":
    asyncio.run(verify_qdrant())
