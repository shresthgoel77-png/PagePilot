import os
import logging
from typing import List, Dict, Any, Optional
from app.services.embeddings import EmbeddingService
from app.services.vector_store import VectorStoreService

logger = logging.getLogger("researchos.retrieval")

# Reranking is now disabled (local ML dependencies uninstalled)

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
        qdrant_results = self.vector_store.search(
            project_id=project_id,
            query_vector=query_vector,
            limit=top_k,
            pdf_ids=pdf_ids
        )
        logger.info(f"Fetched {len(qdrant_results)} candidates from Qdrant")
        
        if not qdrant_results:
            return []
            
        final_results = qdrant_results[:final_k]
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
