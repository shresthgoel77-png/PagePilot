import time
import asyncio
import httpx
import psutil
import os
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.pdf import PDF
from app.services.vector_store import VectorStoreService, qdrant_client

BASE_URL = "http://localhost:8000"
HEADERS = {"Authorization": "Bearer MOCK_TOKEN"}

async def main():
    print("Starting Strict State Sequence & Environment Safety Audit...")

    process = psutil.Process()
    base_ram = process.memory_info().rss
    peak_ram = base_ram

    start_time = time.time()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(f"{BASE_URL}/projects/", headers=HEADERS, json={"name": "Eval Strict Project", "description": "Test"})
        project_id = r.json()["id"]
        
        with open("e2e_valid.pdf", "rb") as f:
            files = {"file": ("e2e_valid.pdf", f, "application/pdf")}
            up_start = time.time()
            r = await client.post(f"{BASE_URL}/projects/{project_id}/pdfs", headers=HEADERS, files=files)
            up_time = time.time() - up_start
            
        pdf_id = r.json()["id"]
        print(f"File Output API Upload Response Native Time: {up_time:.2f} seconds.")
        
        states = []
        last_state = None
        while True:
            cur_ram = process.memory_info().rss
            if cur_ram > peak_ram:
                peak_ram = cur_ram

            r = await client.get(f"{BASE_URL}/projects/{project_id}/pdfs/{pdf_id}/status", headers=HEADERS)
            data = r.json()
            status = data["status"]
            
            if status != last_state:
                states.append(status)
                last_state = status
                print(f"New state sequence transition: {status} | Progress: {data['progress']}")
            
            if status == "ready" or status == "error":
                if status == "error":
                    print(f"ERROR: {data['error_message']}")
                break
            await asyncio.sleep(2)
            
        duration = time.time() - start_time
        print(f"\nCompleted in {duration:.2f} seconds.")
        print(f"Verified Extracted State sequence: {states}")
        print(f"Memory Diagnostics: Base RAM: {base_ram / 1024 / 1024:.2f}MB, Peak RAM: {peak_ram / 1024 / 1024:.2f}MB")
        
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(PDF).where(PDF.id == pdf_id))
        pdf = res.scalar_one_or_none()
        print(f"\nDatabase Output Analysis Results:")
        print(f"  Input Page Count IN: {pdf.page_count}")
        print(f"  Processed State Recorded: {pdf.status.value}")
        
    filter_must = [{"key": "pdf_id", "match": {"value": pdf_id}}]
    chunk_res = qdrant_client.count(
        collection_name=VectorStoreService.COLLECTION_NAME,
        count_filter={"must": filter_must}
    )
    print(f"  Final Qdrant Vectors Count: {chunk_res.count}")

if __name__ == "__main__":
    asyncio.run(main())
