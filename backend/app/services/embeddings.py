import os
import logging
from typing import List, Dict, Any
from app.services.vector_store import VectorStoreService

logger = logging.getLogger("researchos.embeddings")

from google import genai
from app.core.config import settings

class EmbeddingService:
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.batch_size = int(os.getenv("EMBEDDING_BATCH_SIZE", "32"))
        self._client = None
        try:
            self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
        except Exception as e:
            logger.warning(f"Gemini client unavailable, embeddings will use zero vectors: {e}")

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        if not self._client:
            return [[0.0] * 768 for _ in texts]
            
        try:
            response = self._client.models.embed_content(
                model="text-embedding-004",
                contents=texts
            )
            return [emb.values for emb in response.embeddings]
        except Exception as e:
            logger.error(f"Gemini embedding generation failed: {e}")
            raise

    def index_pdf_chunks(self, pdf_id: str, chunks: List[Dict[str, Any]]):
        if not chunks:
            return

        # Idempotency requirement intrinsically tracking vectors implicitly globally flawlessly natively
        self.vector_store.delete_by_pdf(pdf_id)
        
        for i in range(0, len(chunks), self.batch_size):
            batch = chunks[i:i + self.batch_size]
            texts = [c["text"] for c in batch]
            
            vectors = self.generate_embeddings(texts)
            
            upsert_batch = []
            for chunk_data, vector in zip(batch, vectors):
                upsert_batch.append({
                    "vector": vector,
                    "payload": chunk_data
                })
                
            self.vector_store.upsert_chunks(upsert_batch)
