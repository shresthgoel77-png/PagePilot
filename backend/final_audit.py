import asyncio
import httpx
import uuid
import fitz
import asyncpg
import json

BASE_URL = "http://127.0.0.1:8000"
headers = {"Authorization": "Bearer MOCK_TOKEN"}

def generate_complex_pdfs():
    # 1. Multi-page Text PDF
    doc1 = fitz.open()
    page1 = doc1.new_page()
    page1.insert_text((50, 50), "This is text on page 1 that exceeds fifty characters safely to ensure standard OCR logic bypasses efficiently mapping parameters organically.")
    page2 = doc1.new_page()
    page2.insert_text((50, 50), "This is text on page 2 that exceeds fifty characters safely to ensure standard OCR logic bypasses efficiently mapping parameters organically.")
    doc1.save("audit_normal.pdf")
    doc1.close()

    # 2. Pure Scanned/Image PDF
    doc2 = fitz.open()
    page3 = doc2.new_page()
    page3.insert_text((50, 50), "Img")
    page4 = doc2.new_page()
    page4.insert_text((50, 50), "Scanned")
    doc2.save("audit_scanned.pdf")
    doc2.close()
    
    # 3. Mixed PDF
    doc3 = fitz.open()
    page5 = doc3.new_page()
    page5.insert_text((50, 50), "This is text on page 1 that exceeds fifty characters safely verifying logic.")
    page6 = doc3.new_page()
    page6.insert_text((50, 50), "Blank")
    doc3.save("audit_mixed.pdf")
    doc3.close()

async def run_final_audit():
    generate_complex_pdfs()
    
    async with httpx.AsyncClient() as client:
        # Create Project
        resp0 = await client.post(f"{BASE_URL}/projects/", json={"name": "Final Audit Setup", "description": "Rigorous Constraints"}, headers=headers)
        project_id = resp0.json()["id"]
        
        # Upload Normal
        with open("audit_normal.pdf", "rb") as f1:
            r1 = await client.post(f"{BASE_URL}/projects/{project_id}/pdfs", files={"file": ("audit_normal.pdf", f1, "application/pdf")}, headers=headers)
            id_norm = r1.json()["id"]
        
        # Upload Scanned
        with open("audit_scanned.pdf", "rb") as f2:
            r2 = await client.post(f"{BASE_URL}/projects/{project_id}/pdfs", files={"file": ("audit_scanned.pdf", f2, "application/pdf")}, headers=headers)
            id_scan = r2.json()["id"]
            
        # Upload Mixed
        with open("audit_mixed.pdf", "rb") as f3:
            r3 = await client.post(f"{BASE_URL}/projects/{project_id}/pdfs", files={"file": ("audit_mixed.pdf", f3, "application/pdf")}, headers=headers)
            id_mix = r3.json()["id"]
        
        print("Polling status executing structures cleanly natively globally...")
        for _ in range(15):
            s1 = (await client.get(f"{BASE_URL}/projects/{project_id}/pdfs/{id_norm}/status", headers=headers)).json()["status"]
            s2 = (await client.get(f"{BASE_URL}/projects/{project_id}/pdfs/{id_scan}/status", headers=headers)).json()["status"]
            s3 = (await client.get(f"{BASE_URL}/projects/{project_id}/pdfs/{id_mix}/status", headers=headers)).json()["status"]
            
            print(f"Norm:{s1} | Scan:{s2} | Mix:{s3}")
            
            # Note: Mixed will go to `ready` because not ALL pages are OCR! 
            # Prompt 1.3: "An entirely-empty extraction must never be reported as a successful parse" (Scanned). 
            # "A PDF containing both text and nearly-empty pages — verify only the insufficient-text pages are flagged for OCR."
            if s1 == 'ready' and s2 in ['ocr', 'error'] and s3 == 'ready':
                break
            await asyncio.sleep(1)
            
        conn = await asyncpg.connect('postgresql://postgres:postgrespassword@localhost:5432/research_db')
        
        # Test 1: Normal
        row1 = await conn.fetchrow('SELECT parsed_text FROM pdfs WHERE id = $1', id_norm)
        pages1 = json.loads(row1['parsed_text'])
        assert all(not p['needs_ocr'] for p in pages1), "Normal failed OCR checks"
        assert len(pages1) == 2, "Normal missed boundaries"
        
        # Test 2: Scanned
        row2 = await conn.fetchrow('SELECT parsed_text FROM pdfs WHERE id = $1', id_scan)
        pages2 = json.loads(row2['parsed_text'])
        assert all(p['needs_ocr'] for p in pages2), "Scanned failed OCR flags"
        
        # Test 3: Mixed
        row3 = await conn.fetchrow('SELECT parsed_text FROM pdfs WHERE id = $1', id_mix)
        pages3 = json.loads(row3['parsed_text'])
        assert not pages3[0]['needs_ocr'], "Mixed page 1 falsely flagged OCR natively"
        assert pages3[1]['needs_ocr'], "Mixed page 2 failed to flag OCR cleanly"
        
        print("ALL TESTS PASSED: Extracted JSON boundaries map successfully validating Prompt 1.3 completely.")
        await conn.close()

if __name__ == "__main__":
    asyncio.run(run_final_audit())
