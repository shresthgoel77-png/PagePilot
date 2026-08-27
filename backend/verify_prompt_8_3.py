import asyncio
import io
import os
from unittest.mock import patch

# Configure environment for tests
os.environ["CLERK_SECRET_KEY"] = "test_key"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://user:pass@localhost:5432/db"
os.environ["QDRANT_URL"] = "http://localhost:6333"
os.environ["SECRET_KEY"] = "test_secret"
os.environ["UPLOAD_DIR"] = "./uploads"
os.environ["GEMINI_API_KEY"] = "test_gemini"

from fastapi.testclient import TestClient
from app.main import app

def flush_redis():
    # If using memory limits, we may need to make sure we don't have rate limit hits from prior test runs lingering. 
    # Since slowapi limits are memory based here, we just instantiate client
    pass

class MockClerkUser:
    def __init__(self):
        import uuid
        self.id = uuid.uuid4()
        
def get_mock_user():
    return MockClerkUser()
    

from app.core.clerk_auth import get_current_user_clerk
app.dependency_overrides[get_current_user_clerk] = get_mock_user

def run_tests():
    from app.core.rate_limit import limiter
    limiter.reset() # Using internal API if one exists, or just send a fresh IP address per test via headers
        
    results = []
    
    with TestClient(app, raise_server_exceptions=False) as client:
        # We also need to mock `verify_project` to avoid breaking when it can't find tracking projects
        with patch('app.routers.pdfs.verify_project') as mock_verify:
            project_id = "00000000-0000-0000-0000-000000000001"
            
            # --- 1. Rate Limiting HTTP 429 ---
            headers = {"X-Forwarded-For": "100.100.100.100"}
            
            # Endpoint has 5/minute limit. Let's make 6 requests.
            # We will use GET /projects/{project_id}/pdfs if it is rate-limited, but actually only POST is explicitly @limiter.limit("5/minute")
            file_data = {"file": ("empty.pdf", b"%PDF-dummy", "application/pdf")}
            for i in range(5):
                # These will pass rate limit, but might fail early validation due to db stuff, but that's fine.
                resp = client.post(f"/projects/{project_id}/pdfs", files={"file": ("empty.pdf", b"%PDF-dummy", "application/pdf")}, headers=headers)
                
            # The 6th request should be 429
            resp_429 = client.post(f"/projects/{project_id}/pdfs", files={"file": ("empty.pdf", b"%PDF-dummy", "application/pdf")}, headers=headers)
            results.append("=== 1. Rate Limit HTTP 429 ===")
            results.append(f"Status Code: {resp_429.status_code}")
            results.append(f"Response: {resp_429.json()}")
            
            # --- 2. Renamed .exe as .pdf ---
            # Reset rate limits by clearing internal memory storage
            try:
                from app.core.rate_limit import limiter
                from limits.storage import MemoryStorage
                if isinstance(limiter._storage, MemoryStorage):
                    limiter._storage.storage.clear()
            except Exception:
                pass
                
            headers2 = {"X-Forwarded-For": "200.200.200.200"}
            exe_content = b"MZ\x90\x00\x03\x00\x00\x00\x04This is a mocked exe payload"
            with patch('app.routers.pdfs.pg_insert') as mock_insert, patch('fitz.open') as mock_fitz:
                resp_400 = client.post(
                    f"/projects/{project_id}/pdfs",
                    files={"file": ("spoof.pdf", exe_content, "application/pdf")},
                    headers=headers2
                )
                
                results.append("\n=== 2. Renamed .exe as .pdf ===")
                results.append(f"Status Code: {resp_400.status_code}")
                results.append(f"Response: {resp_400.json()}")
                results.append(f"Ingestion Enqueued (pg_insert called): {mock_insert.called}")
                results.append(f"Fitz Parsed (fitz.open called): {mock_fitz.called}")
                
            # --- 3. Oversized PDF > 10MB ---
            try:
                from app.core.rate_limit import limiter
                from limits.storage import MemoryStorage
                if isinstance(limiter._storage, MemoryStorage):
                    limiter._storage.storage.clear()
            except Exception:
                pass
            headers3 = {"X-Forwarded-For": "300.300.300.300"}
            # Mock a file > 10MB but tell the multipart parsing it has a matching size constraint (in memory payload could crash tests)
            # Instead of a huge mock file, we use `file.size` explicitly mapped, or we can just upload 11MB of dummy data buffer.
            # We'll just generate an 11MB byte string memory view to ensure chunking catches it if the size header is omitted, but we provide it inside UploadFile
            huge_content = b"%PDF-" + b"0" * (10 * 1024 * 1024 + 500)
            with patch('app.routers.pdfs.pg_insert') as mock_insert, patch('fitz.open') as mock_fitz:
                resp_413 = client.post(
                    f"/projects/{project_id}/pdfs",
                    files={"file": ("huge.pdf", huge_content, "application/pdf")},
                    headers=headers3
                )
                
                results.append("\n=== 3. Oversized file (10MB limit) ===")
                results.append(f"Status Code: {resp_413.status_code}")
                results.append(f"Response: {resp_413.json()}")
                results.append(f"Ingestion Enqueued (pg_insert called): {mock_insert.called}")
                
            with open("verify_hardening_output.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(results))
            print("Execution tracking explicitly dumped to verify_hardening_output.txt")
            print("\n".join(results))

if __name__ == "__main__":
    run_tests()
