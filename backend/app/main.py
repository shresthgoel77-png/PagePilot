import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

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
    allow_origins=settings.FRONTEND_URLS,
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
from app.routers import auth, projects, pdfs
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(pdfs.router)
