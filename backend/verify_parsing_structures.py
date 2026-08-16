import asyncio
import os
import httpx
import uuid
import time
import fitz

BASE_URL = "http://127.0.0.1:8000"
headers = {"Authorization": "Bearer MOCK_TOKEN"}

def generate_pdfs():
    # 1. Generate Normal Text PDF
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "This is page 1 containing structurally sufficient text mimicking organic contexts directly resolving limits effectively accurately passing bounds natively tracking algorithms securely.")
    page2 = doc.new_page()
    page2.insert_text((50, 50), "This is page 2 with more text exceeding 50 chars mimicking organic contexts directly resolving limits effectively accurately passing bounds natively tracking algorithms securely.")
    doc.save("normal_text.pdf")
    doc.close()

    # 2. Generate Empty Scanned PDF
    doc2 = fitz.open()
    page3 = doc2.new_page()
    page3.insert_text((50, 50), "Img")
    page4 = doc2.new_page()
    page4.insert_text((50, 50), "Scanned")
    doc2.save("scanned_image.pdf")
    doc2.close()

async def verify_parsing():
    generate_pdfs()
    
    async with httpx.AsyncClient() as client:
        # Create Project
        resp0 = await client.post(f"{BASE_URL}/projects/", json={"name": "Verification Setup", "description": "Parsing Hooks"}, headers=headers)
        project_id = resp0.json()["id"]
        
        # Upload Normal
        with open("normal_text.pdf", "rb") as f1:
            resp1 = await client.post(f"{BASE_URL}/projects/{project_id}/pdfs", files={"file": ("normal_text.pdf", f1, "application/pdf")}, headers=headers)
            print(f"Normal Upload Status: {resp1.status_code}")
            print(f"Normal Upload Body: {resp1.text}")
            valid_pdf_id = resp1.json().get("id")
        
        # Upload Scanned
        with open("scanned_image.pdf", "rb") as f2:
            resp2 = await client.post(f"{BASE_URL}/projects/{project_id}/pdfs", files={"file": ("scanned_image.pdf", f2, "application/pdf")}, headers=headers)
            print(f"Scanned Upload Status: {resp2.status_code}")
            print(f"Scanned Upload Body: {resp2.text}")
            scanned_pdf_id = resp2.json().get("id")
        
        # Poll Limits
        print("Polling execution matrices natively wrapping structures...")
        for i in range(15):
            r1 = await client.get(f"{BASE_URL}/projects/{project_id}/pdfs/{valid_pdf_id}/status", headers=headers)
            r2 = await client.get(f"{BASE_URL}/projects/{project_id}/pdfs/{scanned_pdf_id}/status", headers=headers)
            
            d1 = r1.json()
            d2 = r2.json()
            
            print(f"Normal: {d1.get('status')} | Scanned: {d2.get('status')}")
            
            if d1.get('status') == 'ready' and d2.get('status') in ['ocr', 'error']:
                print("--- VALIDATION PASSED ---")
                
                # Assert parsed_text array structure 
                import asyncpg
                import json
                conn = await asyncpg.connect('postgresql://postgres:postgrespassword@localhost:5432/research_db')
                
                row = await conn.fetchrow('SELECT parsed_text FROM pdfs WHERE id = $1', valid_pdf_id)
                pages = json.loads(row['parsed_text'])
                
                assert len(pages) == 2, "Expected 2 explicitly structured JSON limits seamlessly."
                assert pages[0]["page"] == 1 and not pages[0]["needs_ocr"]
                assert pages[1]["page"] == 2 and not pages[1]["needs_ocr"]
                
                row_scan = await conn.fetchrow('SELECT parsed_text, error_message FROM pdfs WHERE id = $1', scanned_pdf_id)
                scan_pages = json.loads(row_scan['parsed_text'])
                
                assert len(scan_pages) == 2, "Expected empty geometries to still execute structuring cleanly!"
                assert scan_pages[0]["needs_ocr"] and scan_pages[1]["needs_ocr"]
                assert row_scan['error_message'] is not None
                
                print("All Database Structures Verified!")
                await conn.close()
                return
                
            await asyncio.sleep(1)

        print("Validation tracking TIMEOUT bounds unexpectedly terminating...")

if __name__ == "__main__":
    asyncio.run(verify_parsing())
