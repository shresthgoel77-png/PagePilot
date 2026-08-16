import fitz
import os

print("Generating 120-page PDF...")
doc = fitz.open()
for i in range(120):
    page = doc.new_page()
    if i % 10 == 0:
        # Create an image-only page (no text layer) to trigger OCR
        # We will draw a rect, EasyOCR might not find text but it shouldn't crash
        page.draw_rect(fitz.Rect(50, 50, 100, 100), color=(0,0,0), fill=(0,0,0))
    else:
        # Regular text page
        page.insert_text((50, 50), f"Regular text page {i+1}. " * 20)

doc.save("e2e_valid.pdf")
doc.close()
print("Saved e2e_valid.pdf", os.path.getsize("e2e_valid.pdf"), "bytes")
