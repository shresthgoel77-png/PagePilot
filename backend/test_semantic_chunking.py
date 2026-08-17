import sys
import os

# Append current dir to sys.path to resolve 'app' module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.pdf_parser import PDFParserService

def test_chunking():
    # We will test using 'audit_normal.pdf' assuming it has multiple sentences.
    pdf_path = "e2e_valid.pdf"
    if not os.path.exists(pdf_path):
        print(f"Test pdf {pdf_path} not found.")
        return

    parser = PDFParserService()
    # Override size for easier testing if we want small chunks, but default 1000 is fine
    parser.chunk_size = 500
    parser.chunk_overlap = 100
    
    gen = parser.parse_pdf_generator(
        pdf_id="test_id_123",
        project_id="proj_1",
        filename="e2e_valid.pdf",
        file_path=pdf_path
    )
    
    total_chunks = 0
    for page_data, page_chunks in gen:
        print(f"--- Page {page_data['page']} ---")
        for chunk in page_chunks:
            total_chunks += 1
            if total_chunks > 5:
                print(f"Total Chunks tested: {total_chunks - 1}")
                return
            
            text = chunk['text']
            print(f"-- Chunk {chunk['chunk_index']} (Len {len(text)}) --")
            print(f"Metadata: page={chunk['page_number']}, doc_id={chunk['pdf_id']}")
            # Print full chunk instead of truncating to verify sentences
            print(f"Text:\n{text}\n")
    
    print(f"Total Chunks: {total_chunks}")
    
if __name__ == "__main__":
    test_chunking()
