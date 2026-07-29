import os
import logging
from typing import List, Dict, Any, Optional
from app.services.embeddings import EmbeddingService
from app.services.vector_store import VectorStoreService

logger = logging.getLogger("researchos.retrieval")

try:
    from sentence_transformers import CrossEncoder
    os.environ['SENTENCE_TRANSFORMERS_HOME'] = '/root/.cache'
    
    _reranker_model = CrossEncoder("BAAI/bge-reranker-v2-m3", device=os.getenv("MODEL_DEVICE", "cpu"))
except Exception as e:
    logger.warning(f"Dependencies locating reranker constraints completely failed implicitly: {e}")
    _reranker_model = None

class RetrievalService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStoreService()

    def retrieve(self, project_id: str, query: str, top_k: int = 20, final_k: int = 5, pdf_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        # Enforce local explicit parameters tracking nested embeddings locally generating unique targets natively
        query_vectors = self.embedding_service.generate_embeddings([query])
        query_vector = query_vectors[0]
        
        # Enforce search limits capturing wide-net architecture bounding states natively uniquely locally 
        fetch_limit = top_k * 2
        qdrant_results = self.vector_store.search(
            project_id=project_id,
            query_vector=query_vector,
            limit=fetch_limit,
            pdf_ids=pdf_ids
        )
        
        if not qdrant_results:
            return []
            
        if _reranker_model:
            pairs = [[query, result.payload.text] for result in qdrant_results]
            # Standard batch resolution constraints tracking explicitly natively bounding execution loops implicitly natively locally securely
            scores = _reranker_model.predict(pairs, batch_size=8)
            
            for result, score in zip(qdrant_results, scores):
                result.score = float(score)
                
            qdrant_results.sort(key=lambda x: x.score, reverse=True)
            
        final_results = qdrant_results[:final_k]
        return [
            {
                "text": r.payload.text,
                "page_number": r.payload.page_number,
                "pdf_id": r.payload.pdf_id,
                "filename": r.payload.filename,
                "score": r.score,
                "chunk_index": r.payload.chunk_index
            }
            for r in final_results
        ]
