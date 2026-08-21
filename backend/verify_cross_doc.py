import sys
import os
import uuid
import logging
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.context_assembler import ContextAssembler

logging.basicConfig(level=logging.INFO)

def run_verification():
    doc1_id = str(uuid.uuid4())
    doc2_id = str(uuid.uuid4())
    
    # Simulate a scenario where Document A has 4 relevant chunks (scored highly)
    # and Document B has only 2 relevant chunks (scored slightly lower).
    # Before balancing, they would appear as AAAABB.
    # After balancing, it should interleave them: ABABAB, but since B only has 2, it should be ABABAA.
    
    raw_chunks = [
        {"pdf_id": doc1_id, "filename": "PaperA.pdf", "page_number": 1, "text": "Apples are definitely red."},
        {"pdf_id": doc1_id, "filename": "PaperA.pdf", "page_number": 2, "text": "Red is the color of most apples."},
        {"pdf_id": doc1_id, "filename": "PaperA.pdf", "page_number": 3, "text": "We concluded apples cannot be blue."},
        {"pdf_id": doc1_id, "filename": "PaperA.pdf", "page_number": 4, "text": "No blue apples exist."},
        
        {"pdf_id": doc2_id, "filename": "PaperB.pdf", "page_number": 1, "text": "Apples are purely blue in our universe."},
        {"pdf_id": doc2_id, "filename": "PaperB.pdf", "page_number": 2, "text": "The blue apple anomaly was confirmed."},
    ]
    
    print("\n[*] Assembling context up to 30,000 chars...")
    context_str = ContextAssembler.assemble_context(raw_chunks, max_chars=30000)
    
    print("\n--- Resulting Context XML Boundaries ---")
    print(context_str)
    print("----------------------------------------")
    
    # Parse the output to extract the order of pdf_ids
    import re
    matches = re.finditer(r'pdf_id="([^"]+)"', context_str)
    order = [m.group(1) for m in matches]
    
    print(f"\n[*] Extracted document interleaved order: {order}")
    
    # Validate the Round-Robin order
    # Expected: DocA, DocB, DocA, DocB, DocA, DocA
    assert len(order) == 6, "Should contain all 6 chunks"
    assert order[0] == doc1_id, "1st chunk must be DocA"
    assert order[1] == doc2_id, "2nd chunk must be DocB (balanced!)"
    assert order[2] == doc1_id, "3rd chunk must be DocA"
    assert order[3] == doc2_id, "4th chunk must be DocB (balanced!)"
    assert order[4] == doc1_id, "5th chunk must be DocA"
    assert order[5] == doc1_id, "6th chunk must be DocA"
    
    print("\n✅ Verification Passed! Cross-Document Balancing forces LLM comparison visibility accurately.")


if __name__ == "__main__":
    run_verification()
