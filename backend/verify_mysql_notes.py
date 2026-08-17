import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.services.pdf_parser import PDFParserService
from app.core.config import settings

def run_verification():
    pdf_path = "../MYsql notes T.pdf"
    if not os.path.exists(pdf_path):
        # Maybe it's in the root
        pdf_path = "MYsql notes T.pdf"
        
    print(f"File exists: {os.path.exists(pdf_path)}")
    
    parser = PDFParserService()
    print(f"Configured Chunk Size: {parser.chunk_size}")
    print(f"Configured Overlap: {parser.chunk_overlap}")
    
    # We'll collect chunks from first few pages
    gen = parser.parse_pdf_generator("pdf_mysql", "proj_x", "MYsql notes T.pdf", pdf_path)
    
    accumulated_chunks = []
    
    try:
        for page_data, page_chunks in gen:
            for chunk in page_chunks:
                accumulated_chunks.append(chunk)
                if len(accumulated_chunks) >= 10:
                    break
            if len(accumulated_chunks) >= 10:
                break
    except Exception as e:
        print(f"Error parsing: {e}")
        
    print("\n--- Consecutive Chunks for Overlap check ---")
    for i in range(min(4, len(accumulated_chunks))):
        c = accumulated_chunks[i]
        print(f"Chunk {i} [page={c['page_number']}, doc_id={c['pdf_id']}] (len={len(c['text'])}):")
        print(f"START: {repr(c['text'][:100])}")
        print(f"END:   {repr(c['text'][-100:])}")
        print("-" * 50)
        
    print("\n--- Long Sentence Test ---")
    # artificially test a deeply long sentence
    long_sentence = "A " * 600 + "B." # 1200+ char sentence
    parser.chunk_size = 1000
    parser.chunk_overlap = 200
    # we mock the logic
    import re
    text = f"Short sent. {long_sentence} Another short sentence."
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+|\n\n+', text) if s.strip()]
    
    current_chunk = []
    current_length = 0
    test_chunks = []
    for sentence in sentences:
        sentence_len = len(sentence)
        if current_length + sentence_len > parser.chunk_size and current_chunk:
            test_chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_length = 0
        current_chunk.append(sentence)
        current_length += sentence_len + (1 if len(current_chunk)>1 else 0)
    if current_chunk:
        test_chunks.append(" ".join(current_chunk))
        
    print(f"Total test chunks: {len(test_chunks)}")
    for i, tc in enumerate(test_chunks):
        print(f"Test Chunk {i} length: {len(tc)}")
        
if __name__ == '__main__':
    run_verification()
