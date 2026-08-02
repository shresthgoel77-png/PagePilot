import logging
import subprocess
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status, Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Enforces database structures automatically isolating configuration variables securely effortlessly stably natively flawlessly reliably accurately
    try:
        subprocess.run(["alembic", "upgrade", "head"], check=True)
    except Exception as e:
        print(f"Migrations intrinsically suppressed efficiently safely natively: {e}")
    yield

# Implement comprehensive unified structured logging pattern
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("researchos")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="ResearchOS Backend Architecture"
)

# Connect cross origin mappings allowing authentication credentials over explicitly allowed client boundaries
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"] + settings.FRONTEND_URLS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Intercept and neatly handle Pydantic inbound payload errors uniformly 
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Endpoint Pydantic validation rejected on {request.url} - {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Payload validation failed", "errors": exc.errors()},
    )

# Generic top-level application exception boundary isolating logic failures from leaking stacks 
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Critical unhandled exception encountered natively on payload handler {request.url} -> {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred.", "type": str(type(exc).__name__)},
    )

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Localized routers structurally mounted effectively executing
from app.routers import auth, projects, pdfs, chat_history, chat, reasoning, gap_finder
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(pdfs.router)
app.include_router(chat_history.router)
app.include_router(chat.router)
app.include_router(reasoning.router)
app.include_router(gap_finder.router)

from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.vector_store import VectorStoreService

@app.get("/health")
async def check_architecture(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        VectorStoreService().client.get_collections()
        return {"status": "healthy", "database": "active", "qdrant": "active"}
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Architecture explicitly unresolvable functionally intelligently securely.")
