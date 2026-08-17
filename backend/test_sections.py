import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.services.pdf_parser import PDFParserService

def run_tests():
    parser = PDFParserService()
    
    # 1. Document with clear headings (synthetic)
    doc_structured = "structured_test.pdf"
    import fitz
    dumb = fitz.open()
    p = dumb.new_page()
    p.insert_text((50,50), "MAJOR SECTION ALFA", fontsize=24)
    p.insert_text((50,100), "This is some normal text following the large section.", fontsize=12)
    p.insert_text((50,150), "MINOR SECTION BETA", fontsize=18)
    p.insert_text((50,200), "This is more normal text following another section.", fontsize=12)
    dumb.save(doc_structured)
    dumb.close()

    print(f"--- Structured Doc: {doc_structured} ---")
    gen1 = parser.parse_pdf_generator("pdf_1", "proj", "struct.pdf", doc_structured)
    
    chunks_struct = []
    try:
        for data, chunks in gen1:
            for c in chunks:
                chunks_struct.append(c)
    except Exception as e:
        print("Error on struct:", e)
        
    for i, c in enumerate(chunks_struct):
        print(f"Chunk {i} [page {c['page_number']}]: SECTION='{c['section']}' TEXT={c['text'][:30]}")
        
    # 2. Document without headings
    doc_flat = "audit_normal.pdf"  # This is a flat, generated pdf in the backend dir
    if not os.path.exists(doc_flat):
        import fitz
        dumb = fitz.open()
        dumb.new_page().insert_text((50,50), "This is plain text with no headings " * 20, fontsize=12)
        dumb.save("audit_normal.pdf")
        dumb.close()
        
    print(f"\n--- Flat Doc: {doc_flat} ---")
    gen2 = parser.parse_pdf_generator("pdf_2", "proj", "flat.pdf", doc_flat)
    chunks_flat = []
    try:
        for data, chunks in gen2:
            for c in chunks:
                chunks_flat.append(c)
                if len(chunks_flat) >= 5: break
            if len(chunks_flat) >= 5: break
    except Exception as e:
        print("Error on flat:", e)
        
    for i, c in enumerate(chunks_flat[:3]):
        print(f"Chunk {i} [page {c['page_number']}]: SECTION={repr(c['section'])}")


if __name__ == '__main__':
    run_tests()
