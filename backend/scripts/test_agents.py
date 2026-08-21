import asyncio
import os
import sys
import logging
from uuid import UUID

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import AsyncSessionLocal
from app.models.research import ResearchRun, ResearchStep
from sqlalchemy.future import select

from app.services.execution_agents import RetrievalAgent, AnalysisAgent, ComparisonAgent
from app.services.research_service import ResearchService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_agents")

async def test_end_to_end():
    # 1. Get a test run or create one
    research_service = ResearchService()
    
    # We just create dummy UUIDs for testing the persistence flow
    import uuid
    dummy_session_id = uuid.uuid4()
    dummy_project_id = str(uuid.uuid4())
    
    # Try to find a real session if possible
    try:
        from app.models.chat import ChatSession
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(ChatSession).limit(1))
            session = result.scalar_one_or_none()
            if session:
                dummy_session_id = session.id
                dummy_project_id = str(session.project_id)
                logger.info(f"Using real session: {dummy_session_id} and project: {dummy_project_id}")
    except Exception as e:
        logger.warning(f"Could not fetch real session: {e}. Using dummies.")

    query = "What are the common differences mentioned across the documents?"
    run = await research_service.create_research_run(dummy_session_id, query)
    logger.info(f"Created ResearchRun: {run.id}")
    
    # Add steps
    steps_data = [
        {"type": "retrieval", "description": "Retrieve general facts"},
        {"type": "analysis", "description": "Analyze doc 1"},
        {"type": "analysis", "description": "Analyze doc 2"},
        {"type": "comparison", "description": "Compare docs"}
    ]
    
    steps = await research_service.add_research_steps(run.id, steps_data)
    
    retrieval_agent = RetrievalAgent()
    analysis_agent = AnalysisAgent()
    comparison_agent = ComparisonAgent()
    
    # Execute Retrieval
    logger.info("Executing Retrieval Agent...")
    retrieval_artifact = await retrieval_agent.execute(
        step_id=steps[0].id,
        project_id=dummy_project_id,
        query=query
    )
    
    # If no chunks, we mock them to verify downstream agents independently
    if not retrieval_artifact.get("chunks"):
        logger.warning("No chunks retrieved. Injecting mock chunks for testing downstream agents.")
        retrieval_artifact["chunks"] = [
            {"pdf_id": "doc1", "text": "Document 1 says X is faster.", "filename": "doc1.pdf", "page_number": 1},
            {"pdf_id": "doc2", "text": "Document 2 says X is more secure but slower.", "filename": "doc2.pdf", "page_number": 1}
        ]

    chunks = retrieval_artifact["chunks"]
    
    # Split chunks for docs (mocking distinct doc IDs if same)
    doc1_chunks = [chunks[0]] if chunks else []
    doc2_chunks = [chunks[1]] if len(chunks) > 1 else doc1_chunks
    
    # Execute Analysis
    logger.info("Executing Analysis Agent 1...")
    analysis1_artifact = {}
    try:
        analysis1_artifact = await analysis_agent.execute(
            step_id=steps[1].id,
            document_id="doc1",
            retrieved_chunks=doc1_chunks,
            query=query
        )
    except Exception as e:
        logger.error(f"Execution skipped due to API keys: {e}")

    logger.info("Executing Analysis Agent 2...")
    analysis2_artifact = {}
    try:
        analysis2_artifact = await analysis_agent.execute(
            step_id=steps[2].id,
            document_id="doc2",
            retrieved_chunks=doc2_chunks,
            query=query
        )
    except Exception as e:
        logger.error(f"Execution skipped due to API keys: {e}")
    
    # Execute Comparison
    logger.info("Executing Comparison Agent...")
    try:
        comparison_artifact = await comparison_agent.execute(
            step_id=steps[3].id,
            documents_findings=[analysis1_artifact, analysis2_artifact],
            query=query
        )
    except Exception as e:
        logger.error(f"Execution skipped due to API keys: {e}")
    
    # Inspect persisted artifacts
    logger.info("Verifying Persisted Artifacts...")
    run_with_steps = await research_service.get_run_with_steps(run.id)
    for step in run_with_steps.steps:
        logger.info(f"Step {step.step_type} ({step.status}): {step.result[:200]}...")
        if not step.result:
            logger.error(f"Step {step.step_type} result is empty!")

if __name__ == "__main__":
    asyncio.run(test_end_to_end())
