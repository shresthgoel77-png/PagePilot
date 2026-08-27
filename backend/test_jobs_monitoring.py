import asyncio
import os
from unittest.mock import patch, MagicMock, AsyncMock
from uuid import uuid4
from datetime import datetime

os.environ["CLERK_SECRET_KEY"] = "test_key"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://user:pass@localhost:5432/db"
os.environ["SECRET_KEY"] = "test_secret"
os.environ["UPLOAD_DIR"] = "./uploads"
os.environ["GEMINI_API_KEY"] = "test_gemini"

from fastapi.testclient import TestClient
from app.main import app
from app.core.clerk_auth import get_current_user_clerk
from app.db.session import get_db

# Override Auth
def dummy_auth():
    user = MagicMock()
    user.id = uuid4()
    return user

app.dependency_overrides[get_current_user_clerk] = dummy_auth


def dummy_job(status, has_error=False):
    job = MagicMock()
    job.id = uuid4()
    job.pdf_id = uuid4()
    job.project_id = uuid4()
    job.status = status
    job.attempt_count = 1
    job.max_attempts = 3
    job.error_message = "Mock Crash Test" if has_error else None
    job.created_at = datetime(2026, 1, 1, 12, 0)
    job.updated_at = datetime(2026, 1, 1, 12, 5) # 5 minutes
    return job

# Create Mocks for DB
mock_db = AsyncMock()

class MockResult:
    def __init__(self, value, is_scalar=True):
        self.value = value
        self._is_scalar = is_scalar
    def scalar_one(self):
        return self.value
    def scalars(self):
        m = MagicMock()
        m.all.return_value = self.value
        return m

def db_execute_side_effect(stmt, *args, **kwargs):
    # Depending on stmt, return different mocked results simulating queues explicitly inherently!
    q = str(stmt).lower()
    if "where ingestion_jobs.status = :status_1" in q:
        # Check explicit bound params if possible, or just hack parsing string
        # sqlalchemy compiled stmt string representation typically shows bound parameters blindly
        pass
        
    return MockResult(0)   # fallback

app.dependency_overrides[get_db] = lambda: mock_db


client = TestClient(app, raise_server_exceptions=False)

def run_test():
    with patch('app.routers.jobs.AsyncSession') as MockSession:
        pass
        # Wait, inside endpoint it's `db.execute()`. 
        # We can just override get_db which yields `mock_db`!

    # We will simulate 3 jobs pending, 2 in-progress, avg 300 seconds, and 1 failed job explicitly manually returning exact bounds natively intelligently.
    
    # sequence of executions per endpoint route:
    mock_db.execute.side_effect = [
        MockResult(3), # queue depth (pending)
        MockResult(2), # in progress
        MockResult(300.0), # average processing time
        MockResult([dummy_job("failed", True)], is_scalar=False) # recent failures
    ]
    
    resp = client.get("/jobs/monitoring")
    print(resp.status_code)
    print(resp.json())

if __name__ == "__main__":
    run_test()
