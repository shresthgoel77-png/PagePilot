from qdrant_client import QdrantClient
from qdrant_client.http import models

client = QdrantClient(url='http://localhost:6333')
points, _ = client.scroll(
    collection_name='document_chunks',
    limit=100
)

with open('debug_qdrant.txt', 'w') as f:
    for p in points:
        f.write(f"{p.payload.get('pdf_id')} | idx: {p.payload.get('chunk_index')} | len: {len(p.payload.get('text', ''))}\n")
print('Done!')
