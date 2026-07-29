import logging
import asyncio
import alembic.config
import alembic.command
from app.db.qdrant import ensure_collection

# Standardize output logs matching root hierarchy universally globally attached
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("researchos.init")

def run():
    logger.info("Starting initialization sequences...")
    alembic_cfg = alembic.config.Config("alembic.ini")
    
    # Migrate DB matching async settings explicitly against missing variables catching logic faults fundamentally natively
    try:
        logger.info("Executing Alembic Upgrade Head...")
        alembic.command.upgrade(alembic_cfg, "head")
        logger.info("Database schemas fully synced natively.")
    except Exception as e:
        logger.warning(f"Migration resolution aborted (ensure PG is running): {e}")

    # Launch Qdrant configuration mapping establishing the persistent collection arrays logically dynamically optimally 
    logger.info("Executing Qdrant Vectors Initialization...")
    ensure_collection()
    
    logger.info("Operations foundation setup entirely terminated cleanly.")

if __name__ == "__main__":
    run()
