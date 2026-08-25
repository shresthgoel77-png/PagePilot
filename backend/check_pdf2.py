import asyncio
import uuid
import json
from unittest.mock import patch, AsyncMock, MagicMock

import qdrant_client
from qdrant_client.http import models
qc = qdrant_client.QdrantClient(location=":memory:")

qc.create_collection(
    collection_name="document_chunks",
    vectors_config=models.VectorParams(size=3072, distance=models.Distance.COSINE),
    on_disk_payload=True
)

import app.db.qdrant
app.db.qdrant.qdrant_client = qc

from app.services.indexing_pipeline import run as pipeline_run
from eval_harness import create_dense_pdf
from app.services.vector_store import VectorStoreService
from app.services.embeddings import EmbeddingService

async def main():
    project_id = str(uuid.uuid4())
    pdf_id = str(uuid.uuid4())
    filename = "Photosynthesis_Biology.pdf"
    pages = [
        "Photosynthesis is a process used by plants, algae and certain bacteria to harness energy from sunlight and turn it into chemical energy. Here, we describe the basic principles of sunlight conversion and cellular respiration. A foundational understanding of these biological systems is critical for studying ecology.",
        "The light-dependent reactions of photosynthesis take place in the thylakoid membrane. Chlorophyll captures energy from sunlight, which is then used to generate ATP and NADPH. The Calvin cycle, which occurs in the stroma, then utilizes this ATP and NADPH to convert CO2 into sugar.",
        "Environmental factors such as temperature, light intensity, and CO2 concentration significantly affect the rate of photosynthesis. High temperatures can denature the enzymes involved in the Calvin cycle, while low light limits ATP production."
    ]
    
    create_dense_pdf(filename, pages)
    
    mock_db = MagicMock()
    mock_session = AsyncMock()
    mock_db.return_value.__aenter__.return_value = mock_session
    mock_pdf = MagicMock(id=uuid.UUID(pdf_id), project_id=uuid.UUID(project_id), filename=filename, file_path=filename)
    # Wait, pipelline expects pdf.id to be UUID or str? We mock it identically.
    
    status_trace = []
    def set_status(self, val): status_trace.append(str(val))
    type(mock_pdf).status = property(lambda self: status_trace[-1] if status_trace else None, set_status)
    
    mock_session.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=mock_pdf))
    
    print("Ingesting PDF...")
    with patch("app.services.indexing_pipeline.AsyncSessionLocal", new=mock_db):
        await pipeline_run(uuid.UUID(project_id), filename, uuid.UUID(pdf_id))
        
    count = qc.count(collection_name="document_chunks")
    print(f"Qdrant collection 'document_chunks' contains {count.count} points.")
    
    vs = VectorStoreService()
    emb = EmbeddingService()
    query_vector = emb.generate_embeddings(["What are the light reactions in photosynthesis?"])[0]
    
    print(f"\nSearching for project '{project_id}' and pdf '{pdf_id}'...")
    res = vs.search(project_id, query_vector, 5, [pdf_id])
    print(f"Hits with strict UUID: {len(res)}")
    
    print("\nRetrieving ALL payloads manually from Qdrant:")
    all_points = qc.scroll(collection_name="document_chunks", limit=100)[0]
    for p in all_points:
        print(f"ID={p.id} Project={p.payload.get('project_id')} PDF={p.payload.get('pdf_id')} Text='{p.payload.get('text')}'")

if __name__ == "__main__":
    asyncio.run(main())
