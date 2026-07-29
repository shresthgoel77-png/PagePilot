# ResearchOS

ResearchOS relies on four distinct database engines operating in tandem:
- **PostgreSQL 16**: Primary relational store.
- **Redis 7**: High-performance key-value cache and asynchronous queue broker.
- **Qdrant**: Vector database for high-dimensional embeddings.
- **Neo4j 5**: Graph database for citation networks and concept mapping.

## Infrastructure Setup

This monorepo uses Docker Compose to orchestrate the local environment dependencies. 
Make sure you have Docker Desktop (Windows/Mac) or Docker Engine (Linux) installed and running.

### Initialization

1. First, set up your local environment file by copying the example:
   ```bash
   cp .env.example .env
   ```

2. Start the local infrastructure using the provided automation script:
   ```bash
   bash scripts/dev-up.sh
   ```
   This script will automatically load the environment variables, launch Docker Compose in detached mode, and poll the containers until all four database services are completely healthy.

### Tear Down

To stop the containers gracefully, run:
```bash
bash scripts/dev-down.sh
```

To stop the containers **and** wipe all persisted database states (cleaning volumes), append the `--volumes` flag:
```bash
bash scripts/dev-down.sh --volumes
```

## Verification

Once the infrastructure is up and scripts complete, you can verify access:
- **Qdrant Dashboard**: Access at [http://localhost:6333/dashboard](http://localhost:6333/dashboard)
- **Neo4j Browser**: Access at [http://localhost:7474](http://localhost:7474) and login using the credentials found in `.env` (default is user `neo4j` and password `researchos_password`).
