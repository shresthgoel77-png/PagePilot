import logging
from qdrant_client import QdrantClient
from qdrant_client.http import models
from app.core.config import settings

logger = logging.getLogger("researchos.qdrant")

qdrant_client = None
try:
    qdrant_client = QdrantClient(url=settings.QDRANT_URL, api_key=getattr(settings, 'QDRANT_API_KEY', None))
except Exception as e:
    logger.error(f"Failed to instantiate Qdrant singleton globally: {e}")

def ensure_collection():
    if not qdrant_client:
        logger.error("Skipping collection construction setup since client is unconnected.")
        return
        
    collection_name = "document_chunks"
    try:
        collections_response = qdrant_client.get_collections()
        exists = any(col.name == collection_name for col in collections_response.collections)
        
        if not exists:
            qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=3072,
                    distance=models.Distance.COSINE
                ),
                on_disk_payload=True
            )
            logger.info(f"Qdrant configured missing '{collection_name}' optimally.")
        else:
            logger.info(f"Qdrant collection '{collection_name}' already exists.")
    except Exception as e:
        logger.error(f"Error interrogating Qdrant indexing: {e}")
