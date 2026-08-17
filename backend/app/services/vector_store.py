import time
import logging
import uuid
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from qdrant_client.http import models
from app.db.qdrant import qdrant_client

logger = logging.getLogger("researchos.vector_store")

class ChunkPayload(BaseModel):
    project_id: str
    pdf_id: str
    page_number: int
    chunk_index: int
    text: str
    filename: str
    type: str = "chunk"
    is_ocr: bool = False
    section: Optional[str] = None

class SearchResult(BaseModel):
    id: str
    score: float
    payload: ChunkPayload

class VectorStoreService:
    COLLECTION_NAME = "document_chunks"

    def __init__(self):
        if not qdrant_client:
            raise RuntimeError("Qdrant service is suspended.")
        self.client = qdrant_client

    def _retry_operation(self, operation, *args, **kwargs):
        attempts = 3
        backoff = 1
        for i in range(attempts):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                # Exponential backoff handler executing network-bound resolutions elegantly
                if i == attempts - 1:
                    logger.error(f"Qdrant interaction collapsed critically after {attempts} attempts: {e}")
                    raise
                logger.warning(f"Qdrant interaction warning (attempt {i+1}): {e}. Expanding polling latency {backoff}s...")
                time.sleep(backoff)
                backoff *= 2

    def upsert_chunks(self, chunks: List[Dict[str, Any]]):
        """
        Ingests document embeddings safely typed evaluating vector array floats against nested payload Dict.
        """
        points = []
        for chunk in chunks:
            payload_validated = ChunkPayload(**chunk["payload"]).model_dump()
            seed_string = f"{payload_validated['project_id']}_{payload_validated['pdf_id']}_{payload_validated['chunk_index']}"
            points.append(
                models.PointStruct(
                    id=str(uuid.uuid5(uuid.NAMESPACE_DNS, seed_string)),
                    vector=chunk["vector"],
                    payload=payload_validated
                )
            )
            
        def _execute():
            self.client.upsert(
                collection_name=self.COLLECTION_NAME,
                points=points
            )
            
        self._retry_operation(_execute)
        
    def search(self, project_id: str, query_vector: List[float], limit: int = 10, pdf_ids: Optional[List[str]] = None) -> List[SearchResult]:
        must_filters = [
            models.FieldCondition(key="project_id", match=models.MatchValue(value=project_id))
        ]
        
        if pdf_ids:
            must_filters.append(
                models.FieldCondition(key="pdf_id", match=models.MatchAny(any=pdf_ids))
            )
            
        query_filter = models.Filter(must=must_filters)
        
        def _execute():
            res = self.client.query_points(
                collection_name=self.COLLECTION_NAME,
                query=query_vector,
                query_filter=query_filter,
                limit=limit
            )
            return res.points
            
        results = self._retry_operation(_execute)
        return [SearchResult(id=str(r.id), score=r.score, payload=ChunkPayload(**r.payload)) for r in results]
        
    def get_all_ids_for_pdf(self, pdf_id: str) -> List[str]:
        def _execute():
            res = self.client.scroll(
                collection_name=self.COLLECTION_NAME,
                scroll_filter=models.Filter(must=[models.FieldCondition(key="pdf_id", match=models.MatchValue(value=pdf_id))]),
                limit=10000 
            )
            return [str(p.id) for p in res[0]]
        return self._retry_operation(_execute)

    def delete_points(self, point_ids: List[str]):
        if not point_ids: return
        def _execute():
            self.client.delete(
                collection_name=self.COLLECTION_NAME,
                points_selector=models.PointIdsList(points=point_ids)
            )
        self._retry_operation(_execute)

    def delete_by_pdf(self, pdf_id: str):
        def _execute():
            self.client.delete(
                collection_name=self.COLLECTION_NAME,
                points_selector=models.Filter(
                    must=[models.FieldCondition(key="pdf_id", match=models.MatchValue(value=pdf_id))]
                )
            )
        self._retry_operation(_execute)
