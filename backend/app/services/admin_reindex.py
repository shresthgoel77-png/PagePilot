import uuid
from typing import List, Dict, Any
from app.services.vector_store import VectorStoreService
from app.services.embeddings import EmbeddingService
from app.services.pdf_parser import PDFParserService

class AdminReindexService:
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.parser = PDFParserService()
        self.embeddings = EmbeddingService()

    def reindex_pdf(self, pdf_id: str, project_id: str, filename: str, file_path: str, dry_run: bool = True) -> Dict[str, Any]:
        """
        Creates deterministic UUIDv5 boundaries matching the physical chunk array sequences 
        and extracts orphaned points globally isolated.
        """
        existing_ids = self.vector_store.get_all_ids_for_pdf(pdf_id)
        
        gen = self.parser.parse_pdf_generator(pdf_id, project_id, filename, file_path)
        all_chunks = []
        for _, chunks in gen:
            all_chunks.extend(chunks)
            
        new_ids = []
        for chunk in all_chunks:
            seed_string = f"{project_id}_{pdf_id}_{chunk['chunk_index']}"
            new_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, seed_string))
            new_ids.append(new_id)

        existing_set = set(existing_ids)
        new_set = set(new_ids)
        
        adds = list(new_set - existing_set)
        updates = list(new_set & existing_set)
        orphans = list(existing_set - new_set)
        
        metrics = {
            "adds": len(adds),
            "updates": len(updates),
            "removes": len(orphans),
            "dry_run": dry_run
        }
        
        if not dry_run:
            if all_chunks:
                # Iterate in batches to prevent hitting embeddings payload limits
                batch_size = self.embeddings.batch_size
                for i in range(0, len(all_chunks), batch_size):
                    batch = all_chunks[i:i + batch_size]
                    vecs = self.embeddings.generate_embeddings([c["text"] for c in batch])
                    upsert_batch = [{"payload": c, "vector": v} for c, v in zip(batch, vecs)]
                    self.vector_store.upsert_chunks(upsert_batch)
                    
            if orphans:
                self.vector_store.delete_points(orphans)
                
        return metrics
