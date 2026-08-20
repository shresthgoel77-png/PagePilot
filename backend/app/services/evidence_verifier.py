import math
import re
from typing import List, Dict, Any
from app.services.embeddings import EmbeddingService

class EvidenceVerifier:
    def __init__(self):
        self.embedding_service = EmbeddingService()

    def cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        dot_product = sum(x * y for x, y in zip(v1, v2))
        magnitude1 = math.sqrt(sum(x * x for x in v1))
        magnitude2 = math.sqrt(sum(x * x for x in v2))
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        return dot_product / (magnitude1 * magnitude2)

    def split_into_claims(self, text: str) -> List[str]:
        # Remove citation brackets like [Source: filename.pdf, Page 1] to prevent artificial skew
        cleaned_text = re.sub(r'\s*\[Source:.*?\]', '', text)
        
        # Split into sentences based on punctuation followed by a space and a capital letter, or end of string
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', cleaned_text.strip())
        return [s.strip() for s in sentences if len(s.strip()) > 5]

    def verify_claims(self, response: str, retrieved_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not retrieved_chunks:
            return []

        claims = self.split_into_claims(response)
        if not claims:
            return []

        # Get embeddings for all extracted claims
        claim_embeddings = self.embedding_service.generate_embeddings(claims)
        
        # Get embeddings for context chunks
        chunk_texts = [c["text"] for c in retrieved_chunks]
        chunk_embeddings = self.embedding_service.generate_embeddings(chunk_texts)

        results = []
        for i, claim in enumerate(claims):
            c_emb = claim_embeddings[i]
            
            best_sim = 0.0
            best_match = None
            
            # Find the maximally supporting chunk
            for j, ch_emb in enumerate(chunk_embeddings):
                sim = self.cosine_similarity(c_emb, ch_emb)
                if sim > best_sim:
                    best_sim = sim
                    best_match = retrieved_chunks[j]
            
            # Threshold chosen empirically for generic sentence embeddings
            supported = best_sim > 0.65  
            
            res = {
                "claim": claim,
                "supported": supported,
                "confidence": round(best_sim, 4),
                "best_match_filename": best_match["filename"] if best_match else None
            }
            results.append(res)
            
        return results
