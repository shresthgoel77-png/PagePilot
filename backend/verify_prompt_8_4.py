import sys
import subprocess
import os

def test_missing_environment():
    # Remove one required environment variable explicitly 
    env = os.environ.copy()
    if 'CLERK_SECRET_KEY' in env:
        del env['CLERK_SECRET_KEY']
    
    # Hide .env to prevent pydantic from falling back
    if os.path.exists(".env"):
        os.rename(".env", ".env.bak")
        
    try:
        # Try importing the app, which should fail due to Pydantic Settings instantiation constraints
        result = subprocess.run(
            [sys.executable, "-c", "from app.main import app"],
            env=env,
            capture_output=True,
            text=True
        )
    finally:
        if os.path.exists(".env.bak"):
            os.rename(".env.bak", ".env")
    
    if result.returncode != 0 and "CLERK_SECRET_KEY" in result.stderr:
        print("PASS: Missing SECRET_KEY properly crashes app instantiation with explicit Pydantic Field failures")
    else:
        print("FAIL: App did not crash explicitly on missing variable correctly!")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        sys.exit(1)

def test_no_suppressed_migrations():
    # Provide all mock vars internally
    env = os.environ.copy()
    env["CLERK_SECRET_KEY"] = "MOCK"
    env["DATABASE_URL"] = "postgresql+asyncpg://user:pass@localhost:5432/db"
    env["QDRANT_URL"] = "http://localhost:6333"
    env["SECRET_KEY"] = "test_secret"
    env["UPLOAD_DIR"] = "./uploads"
    env["GEMINI_API_KEY"] = "test_gemini"

    test_script_content = """
import asyncio
from app.main import lifespan
from fastapi import FastAPI

app = FastAPI()

async def run_lifespan():
    async with lifespan(app):
        print("APPLICATION_STARTED_NORMALLY")

if __name__ == '__main__':
    asyncio.run(run_lifespan())
    """
    
    with open("temp_runner.py", "w") as f:
        f.write(test_script_content)

    result = subprocess.run(
        [sys.executable, "temp_runner.py"],
        env=env,
        capture_output=True,
        text=True
    )
    
    if os.path.exists("temp_runner.py"):
        os.remove("temp_runner.py")
        
    # We should NOT see "Migrations suppressed" from the old try/catch block
    # or any output indicating migrations run automatically
    if "Migrations suppressed" not in result.stdout and "Migrations suppressed" not in result.stderr:
        if "APPLICATION_STARTED_NORMALLY" in result.stdout:
             print("PASS: Migrations are decoupled from execution execution boundaries appropriately!")
        else:
             print("FAIL: Lifespan failed for other reasons.")
             print(result.stderr)
    else:
        print("FAIL: Automated Migration execution paths persist unmanaged in normal runtime lifespans!")
        sys.exit(1)

if __name__ == '__main__':
    print("=== Configuration Auditing ===")
    test_missing_environment()
    print("\n=== Alembic Setup Auditing ===")
    test_no_suppressed_migrations()
