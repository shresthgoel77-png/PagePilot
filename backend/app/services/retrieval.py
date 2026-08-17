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

    def retrieve(self, project_id: str, query: str, top_k: int = 20, final_k: int = 5, pdf_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        # Enforce local explicit parameters tracking nested embeddings locally generating unique targets natively
        query_vectors = self.embedding_service.generate_embeddings([query])
        query_vector = query_vectors[0]
        
        # Enforce search limits capturing wide-net architecture bounding states natively uniquely locally 
        # We use final_k directly for semantic retrieval search limits, discarding local reranker pipeline constraints
        qdrant_results = self.vector_store.search(
            project_id=project_id,
            query_vector=query_vector,
            limit=final_k,
            pdf_ids=pdf_ids
        )
        
        if not qdrant_results:
            return []
            
        final_results = qdrant_results
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
