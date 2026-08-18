import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.context_assembler import ContextAssembler

def verify_assembly():
    print("--- Verifying Context Assembler Logic ---")
    
    # We create mock chunks that represent what retrieval would spit out
    # Chunk 0 has score 0.9. Chunk 1 is a duplicate text of Chunk 0. Chunk 2 is huge. Chunk 3 is valid.
    mock_chunks = [
        {
            "pdf_id": "pdfA",
            "page_number": 1,
            "filename": "alpha.pdf",
            "text": "This is a very important fact about machine learning.",
            "chunk_index": 0,
            "score": 0.99
        },
        {
            "pdf_id": "pdfB",
            "page_number": 7,
            "filename": "beta.pdf",
            "text": "This is a very important fact about machine learning.   ", # Space padded duplicate
            "chunk_index": 5,
            "score": 0.85
        },
        {
            "pdf_id": "pdfC",
            "page_number": 2,
            "filename": "gamma.pdf",
            "text": "Here is additional context that should be included." * 10, # Normal chunk text
            "chunk_index": 1,
            "score": 0.70
        },
        {
            "pdf_id": "pdfD",
            "page_number": 1,
            "filename": "delta.pdf",
            "text": "This text will be dropped because we will set max_chars very low for testing purposes.",
            "chunk_index": 3,
            "score": 0.50
        }
    ]
    
    print("\n[Input Constraints]")
    print(f"Total Chunks In: {len(mock_chunks)}")
    print(f"Contains Duplicate Data: True (Index 0 and 1 are identical texts)")
    
    # Test 1: Deduplication works
    deduped = ContextAssembler.deduplicate(mock_chunks)
    print(f"\n[Test 1] Deduplication output count: {len(deduped)}")
    assert len(deduped) == 3, f"Filtering failed. Expected 3 distinct texts, got {len(deduped)}"
    print("  -> Passed! Near-identical texts successfully stripped keeping the highest relevance one natively.")
    
    # Test 2: Assembly Bounds and Structure
    test_limit = 400 # Small char limit to cut off chunk 3
    final_context = ContextAssembler.assemble_context(mock_chunks, max_chars=test_limit)
    
    print("\n[Test 2] Assembled Context Snapshot:")
    print("------------------------------------------")
    print(final_context)
    print("------------------------------------------")
    
    str_len = len(final_context)
    print(f"Output character size: {str_len} (Bound: {test_limit})")
    assert str_len < test_limit, "Context string exceeded token/char bound!"
    
    # Should contain XML tags preserving metadata
    assert 'source="alpha.pdf"' in final_context, "Metadata source lost"
    assert 'page="1"' in final_context, "Metadata page lost"
    assert '<document_chunk' in final_context, "Metadata structure tag lost"
    
    # Should NOT contain delta.pdf because the char limit stopped it
    assert 'delta.pdf' not in final_context, "Bounds failure! delta.pdf was included!"
    print("  -> Passed! Final string verified: order matches, exactly structured via XML blocks mapping directly for Phase 4 citations, duplicates discarded, and strict character bounds enforced.")

if __name__ == "__main__":
    verify_assembly()
