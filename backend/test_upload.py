import httpx
import asyncio

async def test_upload():
    # First get or create a project
    async with httpx.AsyncClient() as client:
        # Create project
        resp = await client.post("http://localhost:8000/projects/", 
            headers={"Authorization": "Bearer MOCK_TOKEN"},
            json={"name": "Test Project", "description": "Test"}
        )
        if resp.status_code != 201:
            print("Failed creating project", resp.text)
            return
            
        proj_id = resp.json()["id"]
        print("Project created:", proj_id)
        
        # Test PDF upload
        with open("test.pdf", "wb") as f:
            f.write(b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF")
            
        with open("test.pdf", "rb") as f:
            files = {"file": ("test.pdf", f, "application/pdf")}
            resp = await client.post(f"http://localhost:8000/projects/{proj_id}/pdfs",
                headers={"Authorization": "Bearer MOCK_TOKEN"},
                files=files
            )
            print("Upload Response:", resp.status_code, resp.text)

if __name__ == "__main__":
    asyncio.run(test_upload())
