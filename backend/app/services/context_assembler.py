from typing import List, Dict, Any
import logging
import json

logger = logging.getLogger("researchos.context_assembler")

class ContextAssembler:
    """
    Assembles vector-retrieved chunks into the final string/set of objects passed into the LLM system context.
    Enforces highest-relevance ordering inherently (maintains order passed to it), 
    drops deduplicates, preserves explicit metadata boundaries (XML/JSON structured), 
    and limits total character size to prevent LLM hallucination/bloat.
    """
    
    @staticmethod
    def deduplicate(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        unique_chunks = []
        seen_texts = set()
        
        for c in chunks:
            # We strictly deduplicate on the exact lowercased stripped string. 
            # Could be upgraded to MinHash/Jaccard if needed, but exact text matching solves identical overlap from redundant PDFs.
            text_signature = c.get('text', '').strip().lower()
            if text_signature not in seen_texts:
                seen_texts.add(text_signature)
                unique_chunks.append(c)
            else:
                logger.info(f"Dropped duplicate candidate chunk from {c.get('filename')} page {c.get('page_number')}")
        
        return unique_chunks

    @staticmethod
    def assemble_context(chunks: List[Dict[str, Any]], max_chars: int = 30000) -> str:
        """
        Takes raw dictionaries, deduplicates them, and structures them deliberately into stringified JSON 
        or clear XML blocks up to a max_chars constraint. Returns the context string.
        """
        clean_chunks = ContextAssembler.deduplicate(chunks)
        
        structured_context_parts = []
        current_chars = 0
        
        for i, c in enumerate(clean_chunks):
            # Using XML-like tags forces the LLM to structurally isolate the blocks and citation bounds correctly natively
            # instead of collapsing them into a flat blob.
            chunk_str = (
                f'<document_chunk id="{i+1}" source="{c.get("filename", "")}" '
                f'page="{c.get("page_number", "")}" pdf_id="{c.get("pdf_id", "")}">\n'
                f'{c.get("text", "")}\n'
                f'</document_chunk>\n'
            )
            
            chunk_length = len(chunk_str)
            if current_chars + chunk_length > max_chars:
                logger.warning(f"Context bounds reached ({max_chars}). Dropping lower-relevance chunks.")
                break
                
            structured_context_parts.append(chunk_str)
            current_chars += chunk_length
            
        final_string = "\n".join(structured_context_parts)
        return final_string
