import logging
import io
import easyocr
import threading

logger = logging.getLogger("researchos.ocr_service")

# Global singleton ensuring models aren't reloaded repeatedly
_reader_lock = threading.Lock()
_reader = None

def get_easyocr_reader():
    global _reader
    if _reader is None:
        with _reader_lock:
            if _reader is None:
                logger.info("Initializing EasyOCR Engine mapping organically...")
                # Download and execute English layout
                _reader = easyocr.Reader(['en'], gpu=False) # Safely defaults to CPU
    return _reader

class OCRService:
    def __init__(self):
        self.reader = get_easyocr_reader()

    def extract_text(self, image_bytes: bytes) -> str:
        """Executes a synchronous OCR extraction targeting fully isolated PyTorch evaluation natively decoupling explicitly LLM execution bugs."""
        try:
            # EasyOCR natively supports bytes
            results = self.reader.readtext(image_bytes)
            # Extracted list of (bbox, text, prob)
            extracted_strings = [res[1] for res in results]
            text = " ".join(extracted_strings)
            
            if not text.strip():
                logger.warning("Empty evaluation bound triggered natively resolving constraints globally!")
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Native offline OCR execution failed natively binding: {e}")
            raise RuntimeError(f"Authentic OCR Corruption Error: {str(e)}")
