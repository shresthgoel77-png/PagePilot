import sys
import os
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.services.vector_store import ChunkPayload
from pydantic import ValidationError

def test_pydantic_legacy_schema():
    # A chunk from before Prompt 2.3 (missing `type`, `is_ocr`, `section`)
    legacy_payload = {
        "project_id": "proj_xyz",
        "pdf_id": "pdf_123",
        "page_number": 1,
        "chunk_index": 0,
        "text": "This is legacy content extracted previously.",
        "filename": "old_doc.pdf"
    }

    print("--- Legacy Payload Passed to Pydantic (Retrieval Mock) ---")
    try:
        validated = ChunkPayload(**legacy_payload)
        dump = validated.model_dump()
        print(json.dumps(dump, indent=2))
        assert dump["type"] == "chunk", "Type should default to 'chunk'"
        assert dump["is_ocr"] == False, "is_ocr should default to False"
        assert dump["section"] == None, "section should default to None"
        print("PASS: Legacy payloads are parsed gracefully without runtime errors.\n")
    except ValidationError as e:
        print("FAIL: Legacy payload caused validation error!")
        print(e)
        return

def test_new_document_insertion_schema():
    from app.services.pdf_parser import PDFParserService
    parser = PDFParserService()
    
    # Generate some chunks
    print("--- New Payload Generation from Pipeline (Write Mock) ---")
    gen = parser.parse_pdf_generator(pdf_id="new_pdf_456", project_id="proj_xyz", filename="new_doc.pdf", file_path="../MYsql notes T.pdf")
    
    for page_data, page_chunks in gen:
        if page_chunks:
            chunk = page_chunks[0]
            print(json.dumps(chunk, indent=2))
            
            # Assert all 9 keys exist
            expected_keys = {"project_id", "pdf_id", "page_number", "chunk_index", "text", "filename", "type", "is_ocr", "section"}
            actual_keys = set(chunk.keys())
            
            if expected_keys == actual_keys:
                print("PASS: New generated chunk matches the exact strictly typed schema requirements.")
                assert chunk["type"] == "chunk"
            else:
                print(f"FAIL: Missing keys or extra keys! Detected: {actual_keys}")
        break  # We only need 1 chunk to verify structure

if __name__ == "__main__":
    test_pydantic_legacy_schema()
    test_new_document_insertion_schema()
