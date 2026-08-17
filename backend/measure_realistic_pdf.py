import time
import asyncio
import httpx
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.pdf import PDF
from app.services.vector_store import VectorStoreService, qdrant_client
import json
import sys

BASE_URL = "http://localhost:8000"
HEADERS = {"Authorization": "Bearer MOCK_TOKEN"}

async def main():
    start_time = time.time()
    
    # Pre-flight checks and baseline RAM
    try:
        import psutil
        def get_backend_process():
            for p in psutil.process_iter(['name', 'cmdline']):
                try:
                    cmd = p.info.get('cmdline')
                    if cmd and ('uvicorn' in ' '.join(cmd).lower() or 'app.main' in ' '.join(cmd).lower()):
                        return p
                except:
                    pass
            return None
            
        p = get_backend_process()
        baseline_ram = 0
        if p:
            baseline_ram = p.memory_info().rss / (1024 * 1024)
            print(f"Found baseline RAM: {baseline_ram:.2f} MB")
        else:
            print("Warning: Could not find uvicorn process for RAM tracking.")
    except ImportError:
        print("psutil not installed, RAM tracking disabled")
        p = None
        baseline_ram = 0
        
    import threading
    peak_ram = [baseline_ram]
    running = True

    def monitor_ram():
        while running and p:
            try:
                mem = p.memory_info().rss / (1024 * 1024)
                if mem > peak_ram[0]:
                    peak_ram[0] = mem
                time.sleep(0.5)
            except:
                pass

    threading.Thread(target=monitor_ram, daemon=True).start()

    async with httpx.AsyncClient(timeout=120.0) as client:
        # Create Project
        r = await client.post(f"{BASE_URL}/projects/", headers=HEADERS, json={"name": "Realistic Eval", "description": "Test"})
        project_id = r.json()["id"]
        
        pdf_file = "C:/Users/HP/OneDrive/Desktop/.vscode/gen ai/MYsql notes T.pdf"
        print(f"Uploading {pdf_file}...")
        with open(pdf_file, "rb") as f:
            files = {"file": (pdf_file, f, "application/pdf")}
            up_start = time.time()
            r = await client.post(f"{BASE_URL}/projects/{project_id}/pdfs", headers=HEADERS, files=files)
            upload_latency = time.time() - up_start
            
        pdf_id = r.json()["id"]
        print(f"Upload complete in {upload_latency:.2f}s, PDF ID: {pdf_id}")
        
        state_durations = {}
        states_seen = []
        last_state = "uploaded"
        state_start = time.time()
        
        while True:
            try:
                r = await client.get(f"{BASE_URL}/projects/{project_id}/pdfs/{pdf_id}/status", headers=HEADERS)
                data = r.json()
                status = data["status"]
                
                if status != last_state:
                    dur = time.time() - state_start
                    state_durations[last_state] = dur
                    states_seen.append(last_state)
                    last_state = status
                    state_start = time.time()
                    print(f"Transitioned to {status}, previous state took {dur:.2f}s")
                    
                if status == "ready" or status == "error":
                    # record final state duration
                    states_seen.append(status)
                    state_durations[status] = time.time() - state_start
                    break
            except Exception as e:
                print(f"Error polling status: {e}")
            await asyncio.sleep(0.02)
            
    running = False
    total_duration = time.time() - start_time
    
    # DB Stats
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(PDF).where(PDF.id == pdf_id))
        pdf = res.scalar_one_or_none()
        
        # parsed_text is not populated securely by indexing_pipeline mapping; use native count from DB
        page_count = pdf.page_count or 0
        native_pages = 0
        ocr_pages = 0
        
        # Native/OCR count requires checking the DB if it was updated, but the standard pipeline does not write it back.
        # We will parse it natively here for tracking.
        import fitz
        try:
            doc = fitz.open(pdf_file)
            for page in doc:
                text = page.get_text("text").strip()
                if len(text) < 50:
                    ocr_pages += 1
                else:
                    native_pages += 1
            doc.close()
        except:
            pass
        
    # Chunks
    try:
        filter_must = [{"key": "pdf_id", "match": {"value": pdf_id}}]
        chunk_res = qdrant_client.count(
            collection_name=VectorStoreService.COLLECTION_NAME,
            count_filter={"must": filter_must}
        )
        chunks = chunk_res.count
        
        # Vector info
        q_info = qdrant_client.get_collection(collection_name=VectorStoreService.COLLECTION_NAME)
        vector_dim = q_info.config.params.vectors.size
    except Exception as e:
        print(f"Qdrant error: {e}")
        chunks = 0
        vector_dim = 0
    
    report = []
    report.append("--- REQUIRED OUTPUT ---")
    report.append("PASS/FAIL: " + ("PASS" if last_state == "ready" else "FAIL"))
    report.append(f"PDF: {pdf_file}")
    report.append(f"Pages: {page_count}")
    report.append(f"Native-text pages: {native_pages}")
    report.append(f"OCR/scanned pages: {ocr_pages}")
    report.append(f"Chunks: {chunks}")
    report.append(f"Upload latency: {upload_latency:.2f}s")
    report.append(f"Peak RAM: {peak_ram[0]:.2f} MB")
    report.append(f"RAM increase: {(peak_ram[0] - baseline_ram):.2f} MB")
    report.append(f"Total duration: {total_duration:.2f}s")
    
    for s in ["queued", "parsing", "ocr", "embedding", "indexing"]:
        report.append(f"{s.capitalize()}: {state_durations.get(s, 0.0):.2f}s")
        
    report.append(f"Final state: {last_state}")
    report.append(f"State history: {' -> '.join(states_seen)}")
    report.append(f"Qdrant vectors: {chunks}")
    report.append(f"Vector dimension: {vector_dim}")
    report.append("Failures found: None yet")
    report.append("Fixes made: None yet")
    report.append("Final assessment: Pending")
    
    with open("report.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    print("Report written to report.txt")

if __name__ == "__main__":
    asyncio.run(main())
