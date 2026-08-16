import httpx
import asyncio
import os

BASE_URL = "http://localhost:8000"
HEADERS = {"Authorization": "Bearer MOCK_TOKEN"}

async def wait_for_server():
    async with httpx.AsyncClient() as client:
        for _ in range(20):
            try:
                r = await client.get(f"{BASE_URL}/docs")
                if r.status_code == 200:
                    return
            except httpx.ConnectError:
                pass
            await asyncio.sleep(1)
        raise RuntimeError("Server did not boot")
        
async def e2e_audit():
    print("Waiting for server to boot...")
    await wait_for_server()
    print("Server online. Proceeding with E2E Audit.")

    file_path = "e2e_valid.pdf"
    with open(file_path, "wb") as f:
         f.write(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")

    async with httpx.AsyncClient() as client:
        # Create Project directly using API
        project_req = await client.post(f"{BASE_URL}/projects/", headers=HEADERS, json={"name": "E2E Project", "description": "Test"})
        assert project_req.status_code == 201, f"Project creation failed: {project_req.text}"
        project_id = project_req.json()["id"]
        print(f"Created isolated project: {project_id}")

        # 1. Test POST document directly
        with open(file_path, "rb") as f:
            files = {"file": ("e2e_valid.pdf", f, "application/pdf")}
            r = await client.post(f"{BASE_URL}/projects/{project_id}/pdfs", headers=HEADERS, files=files)
            assert r.status_code == 201, f"POST failed: {r.text}"
            pdf_data = r.json()
            pdf_id = pdf_data["id"]
            print(f"Created PDF {pdf_id} with state {pdf_data['status']}")
            
        # 2. Duplicate upload prevention assertion
        with open(file_path, "rb") as f:
            files2 = {"file": ("e2e_valid.pdf", f, "application/pdf")}
            r2 = await client.post(f"{BASE_URL}/projects/{project_id}/pdfs", headers=HEADERS, files=files2)
            assert r2.status_code == 201, "Duplicate upload failed"
            assert r2.json()["id"] == pdf_id, "Duplicate upload generated new PDF rather than executing deduplication bounds!"
            print("Verified Content DUPLICATE Prevention natively!")
            
        # 3. Test Polling sequence and State Machine mapping
        states_seen = set()
        
        for _ in range(40):
            r = await client.get(f"{BASE_URL}/projects/{project_id}/pdfs/{pdf_id}/status", headers=HEADERS)
            data = r.json()
            status = data["status"]
            states_seen.add(status)
            
            print(f"Poll check -> Status: {status} | Progress: {data['progress']} | Error: {data['error_message']}")
            
            if status in ["ready", "error"]:
                if status == "ready":
                    assert data["progress"] == 100
                    assert data["indexed_at"] is not None
                break
                
            await asyncio.sleep(0.5)
            
        print(f"State Machine Journey Executed: {states_seen}")

if __name__ == "__main__":
    asyncio.run(e2e_audit())
