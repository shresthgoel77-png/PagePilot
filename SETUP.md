# ResearchOS Setup Guide

Welcome to ResearchOS! This step-by-step guide will help you install, configure, and launch the entire application seamlessly on a fresh machine.

## 1. Prerequisites
Ensure you have the following installed on your machine:
* **Docker & Docker Compose**: Required for running the PostgreSQL database, Qdrant vector store, and optionally the backend/frontend containers.
* **Node.js**: Version `>=20.9.0` is strictly required for the Next.js frontend dependencies (Turbopack).
* **Python**: Version `>=3.11` (only necessary if running the backend natively outside Docker).
* **Git**: To clone the repository.

## 2. Environment Variables Configuration
The project expects environment configurations in the root directory to properly route internal logic.
Create a `.env` file (if it doesn't already exist) and populate it with the following expected configuration:

```env
# Full Connection String for Backend (using Docker DNS resolution)
DATABASE_URL=postgresql+asyncpg://postgres:postgrespassword@db:5432/research_db

# Qdrant URL configuration
QDRANT_URL=http://qdrant:6333

# App Settings
SECRET_KEY=super-secret-local-dev-key
UPLOAD_DIR=./uploads

# Gemini configuration (Replace with your actual API key)
GEMINI_API_KEY=your-gemini-api-key-here

# Raw DB credentials (used by the postgres image initialization)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgrespassword
POSTGRES_DB=research_db
```
> **Note on Local Native Executions:** If you choose to run the backend natively (without Docker compress orchestration), you must change `db:5432` to `localhost:5432` and `qdrant:6333` to `localhost:6333` so Python can resolve the ports locally.

## 3. Starting the Backend & Database Services
The easiest and recommended way to start the required infrastructure is via the orchestrated Docker definition.

### Option A: Using the Startup Script (Mac/Linux/WSL)
Execute the provided development startup script in your terminal:
```bash
./scripts/dev-up.sh
```
This script will automatically trigger `docker-compose up -d` and actively poll the `researchos-db` and `researchos-qdrant` containers until they respond with a healthy status.

### Option B: Using Docker Compose Directly (Cross-platform)
Run this command from the root directory:
```bash
docker compose up -d --build
```
This will build and subsequently spin up all four components:
* `researchos-db` (PostgreSQL)
* `researchos-qdrant` (Qdrant Vector DB)
* `researchos-backend` (FastAPI)
* `researchos-frontend` (Next.js)

### Database Migrations
**No manual migration commands are required.** The FastAPI backend (`backend/app/main.py`) is configured with asynchronous lifespan hooks to automatically trigger `alembic upgrade head` upon application boot.

## 4. Starting the Frontend Locally (Development Mode)
If you prefer running the Next.js frontend natively for hot-module reloading rather than through Docker, ensure the backend containers are running first, then execute:
```bash
cd frontend
npm install
npm run dev
```

## 5. Verification Checklist
Verify your startup sequence is healthy by visiting the endpoints:
* [ ] **Frontend UI**: [http://localhost:3000](http://localhost:3000)
* [ ] **Backend Health Check**: [http://localhost:8000/health](http://localhost:8000/health) 
  *(Should output `{"status": "healthy", "database": "active", "qdrant": "active"}`)*
* [ ] **Backend API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
* [ ] **Qdrant Dashboard**: [http://localhost:6333/dashboard](http://localhost:6333/dashboard)

## 6. Common Startup Errors
* **Database / API connection failures (503 Error on Landing Page)**
  * **Cause**: Backend booted faster than the PostgreSQL process could initialize, or your `.env` contains Native Localhost connections (`localhost:5432`) instead of Docker DNS bindings (`db:5432`).
  * **Solution**: View backend error reasons using `docker logs researchos-backend` or reboot the backend container using `docker compose restart backend`. Validate Docker is actively running on your host OS.
* **`Module not found` / Typescript Errors in Frontend Compilation**
  * **Cause**: Next.js 16 compiler rigidly enforces typings and promises on Next parameters. 
  * **Solution**: You can disable strict static validation by assigning `typescript: { ignoreBuildErrors: true }` inside `next.config.mjs` temporarily if nested UI types are dropping your application launches.
* **File Permission or Volume Start Failures**
  * **Cause**: The `./uploads` mount directory specified in `.env` might not exist or lacks read/write boundaries on Windows/Linux environments.
  * **Solution**: Create the directory manually via `mkdir uploads` in your root folder.
  