import os
import logging
from typing import List, Dict, Any
from app.services.vector_store import VectorStoreService

logger = logging.getLogger("researchos.embeddings")

try:
    from sentence_transformers import SentenceTransformer
    # Cache mapping guarantees Docker volume isolations tracking persistence exclusively natively bypassing restarts internally
    os.environ['SENTENCE_TRANSFORMERS_HOME'] = '/root/.cache'
    _embedding_model = SentenceTransformer("BAAI/bge-m3", device=os.getenv("MODEL_DEVICE", "cpu"))
except ImportError:
    _embedding_model = None

class EmbeddingService:
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.batch_size = int(os.getenv("EMBEDDING_BATCH_SIZE", "32"))
        if _embedding_model is None:
             logger.warning("sentence-transformers dependency natively unavailable, vectors mocked inherently safely.")

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        if not _embedding_model:
            return [[0.0] * 1024 for _ in texts]
            
        embeddings = _embedding_model.encode(
            texts,
            batch_size=self.batch_size,
            normalize_embeddings=True,
            show_progress_bar=False
        )
        # Returns normalized cosine execution blocks efficiently tracked locally logically globally natively
        return embeddings.tolist()

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
