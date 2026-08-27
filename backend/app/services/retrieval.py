import os
import logging
from typing import List, Dict, Any, Optional
from app.services.embeddings import EmbeddingService
from app.services.vector_store import VectorStoreService
from app.core.metrics import qdrant_requests_total, qdrant_query_latency_seconds, reranker_requests_total, reranker_latency_seconds

logger = logging.getLogger("researchos.retrieval")

# Optional Reranker Dependency
try:
    from sentence_transformers import CrossEncoder
    cross_encoder_model = CrossEncoder('cross-encoder/ms-marco-TinyBERT-L-2-v2', max_length=512)
    RERANKER_AVAILABLE = True
except Exception as e:
    logger.warning(f"Failed to load sentence_transformers CrossEncoder. Reranking disabled. Error: {e}")
    RERANKER_AVAILABLE = False
    cross_encoder_model = None

class RetrievalService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStoreService()

    def retrieve(self, project_id: str, query: str, top_k: int = 50, final_k: int = 10, pdf_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        # Enforce local explicit parameters tracking nested embeddings locally generating unique targets natively
        query_vectors = self.embedding_service.generate_embeddings([query])
        query_vector = query_vectors[0]
        
        # Enforce search limits capturing wide-net architecture bounding states natively uniquely locally 
        # We use top_k for fetching from VectorStore, leaving room for future rerankers
        logger.info(f"Retrieving top_k={top_k} from Qdrant for query: '{query}'")
        try:
            with qdrant_query_latency_seconds.time():
                qdrant_results = self.vector_store.search(
                    project_id=project_id,
                    query_vector=query_vector,
                    limit=top_k,
                    pdf_ids=pdf_ids
                )
            qdrant_requests_total.labels(status="success").inc()
            logger.info(f"Fetched {len(qdrant_results)} candidates from Qdrant")
        except Exception as e:
            qdrant_requests_total.labels(status="error").inc()
            logger.error(f"Qdrant query crashed explicitly gracefully seamlessly bound intrinsically: {e}")
            raise e
        
        if not qdrant_results:
            return []
            
        final_results = qdrant_results
        
        # --- Phase 3: Reranking ---
        if RERANKER_AVAILABLE and cross_encoder_model:
            try:
                logger.info("Executing CrossEncoder reranking layer...")
                pairs = [(query, r.payload.text) for r in qdrant_results]
                
                with reranker_latency_seconds.time():
                    scores = cross_encoder_model.predict(pairs)
                
                for i, r in enumerate(final_results):
                    r.score = float(scores[i]) 
                final_results.sort(key=lambda x: x.score, reverse=True)
                reranker_requests_total.labels(fallback_triggered="false").inc()
                logger.info("Reranking completed successfully.")
            except Exception as e:
                reranker_requests_total.labels(fallback_triggered="true").inc()
                logger.error(f"Reranking failed explicitly (fallback activated to dense vector ordering). Error: {e}")
                # Revert to original dense search behavior automatically
                final_results = qdrant_results
                
        final_results = final_results[:final_k]
        logger.info(f"Reduced to final_k={final_k} candidates (actual: {len(final_results)}) for LLM context")
        return [
            {
                "project_id": r.payload.project_id,
                "pdf_id": r.payload.pdf_id,
                "page_number": r.payload.page_number,
                "chunk_index": r.payload.chunk_index,
                "text": r.payload.text,
                "filename": r.payload.filename,
                "type": r.payload.type,
                "is_ocr": r.payload.is_ocr,
                "section": r.payload.section,
                "score": r.score
            }
            for r in final_results
        ]
