import time
import asyncio
import httpx
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.pdf import PDF
from app.services.vector_store import VectorStoreService, qdrant_client

BASE_URL = "http://localhost:8000"
HEADERS = {"Authorization": "Bearer MOCK_TOKEN"}

async def main():
    print("Starting Large Document Safety Audit...")
    start_time = time.time()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Create Project
        r = await client.post(f"{BASE_URL}/projects/", headers=HEADERS, json={"name": "Eval Project", "description": "Test"})
        project_id = r.json()["id"]
        
        with open("e2e_valid.pdf", "rb") as f:
            files = {"file": ("e2e_valid.pdf", f, "application/pdf")}
            # Upload (HTTP Request) should return quickly
            up_start = time.time()
            r = await client.post(f"{BASE_URL}/projects/{project_id}/pdfs", headers=HEADERS, files=files)
            up_time = time.time() - up_start
            
        pdf_id = r.json()["id"]
        print(f"Uploaded instantly in {up_time:.2f} seconds. PDF ID: {pdf_id}")
        
        states = []
        last_state = None
        while True:
            r = await client.get(f"{BASE_URL}/projects/{project_id}/pdfs/{pdf_id}/status", headers=HEADERS)
            data = r.json()
            status = data["status"]
            if status != last_state:
                states.append(status)
                last_state = status
            print(f"Status: {status} | Progress: {data['progress']}")
            
            if status == "ready" or status == "error":
                break
            await asyncio.sleep(2)
            
        duration = time.time() - start_time
        print(f"\nProcessing finished in {duration:.2f} seconds.")
        print(f"State transitions observed: {states}")
        
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(PDF).where(PDF.id == pdf_id))
        pdf = res.scalar_one_or_none()
        print(f"Final Page Count in DB: {pdf.page_count}")
        
    # Chunks
    filter_must = [{"key": "pdf_id", "match": {"value": pdf_id}}]
    chunk_res = qdrant_client.count(
        collection_name=VectorStoreService.COLLECTION_NAME,
        count_filter={"must": filter_must}
    )
    print(f"Final Chunks Out: {chunk_res.count}")

if __name__ == "__main__":
    asyncio.run(main())
