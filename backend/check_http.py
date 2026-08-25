from app.db.qdrant import qdrant_client
print("Qdrant Collections natively present:")
for c in qdrant_client.get_collections().collections:
    print(c.name)
if qdrant_client.collection_exists("document_chunks"):
    count = qdrant_client.count(collection_name="document_chunks")
    print(f"Total points in global db chunk table: {count.count}")
    # Just fetch random payloads
    res = qdrant_client.scroll(collection_name="document_chunks", limit=5)
    for p in res[0]:
        print(f"Hit Project={p.payload.get('project_id')} PDF={p.payload.get('pdf_id')} Text='{p.payload.get('text')}'")
