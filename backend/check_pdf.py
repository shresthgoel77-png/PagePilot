import asyncio
import uuid
import json
from unittest.mock import patch, AsyncMock, MagicMock
from app.services.indexing_pipeline import run as pipeline_run
from eval_harness import create_dense_pdf

import qdrant_client
qc = qdrant_client.QdrantClient(location=":memory:")
import app.db.qdrant
app.db.qdrant.qdrant_client = qc
from app.db.qdrant import ensure_collection

async def main():
    ensure_collection()
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
    mock_pdf = MagicMock(id=pdf_id, project_id=project_id, filename=filename, file_path=filename)
    mock_session.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=mock_pdf))
    
    with patch("app.services.indexing_pipeline.AsyncSessionLocal", new=mock_db):
        await pipeline_run(project_id, filename, pdf_id)
        
    count = qc.count(collection_name=project_id)
    print(f"Qdrant collection '{project_id}' contains {count.count} points.")
    
    from app.services.vector_store import VectorStoreService
    vs = VectorStoreService()
    print("Testing manual semantic extraction search:")
    res = vs.search(project_id, vs.model.encode("What are the light reactions in photosynthesis?").tolist(), 5, [pdf_id])
    print(f"Hits: {len(res)}")
    for r in res:
        print(f"  {r.payload.text}")

if __name__ == "__main__":
    asyncio.run(main())
