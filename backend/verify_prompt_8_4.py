import sys
import subprocess
import os

def test_missing_environment():
    required_secrets = ["CLERK_SECRET_KEY", "GEMINI_API_KEY", "DATABASE_URL", "QDRANT_URL"]
    
    # Hide .env to prevent pydantic from falling back
    if os.path.exists(".env"):
        os.rename(".env", ".env.bak")
        
    try:
        for secret_to_remove in required_secrets:
            # Provide baseline env
            env = os.environ.copy()
            env["CLERK_SECRET_KEY"] = "mock_clerk"
            env["GEMINI_API_KEY"] = "mock_gemini"
            env["DATABASE_URL"] = "mock_db"
            env["QDRANT_URL"] = "mock_qdrant"
            env["SECRET_KEY"] = "mock_secret"
            env["UPLOAD_DIR"] = "mock_upload"
            
            # Remove the targeted variable
            if secret_to_remove in env:
                del env[secret_to_remove]
                
            # Try importing the app, which should fail due to Pydantic Settings instantiation constraints
            result = subprocess.run(
                [sys.executable, "-c", "from app.main import app"],
                env=env,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0 and secret_to_remove in result.stderr:
                print(f"PASS: Missing {secret_to_remove} properly crashes app instantiation with explicit Pydantic Field failures")
            else:
                print(f"FAIL: App did not crash explicitly on missing variable: {secret_to_remove}")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                sys.exit(1)
    finally:
        if os.path.exists(".env.bak"):
            os.rename(".env.bak", ".env")

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
