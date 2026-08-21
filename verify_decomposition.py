import asyncio
import json
import os
import sys
from uuid import uuid4

from dotenv import load_dotenv
load_dotenv("c:/Users/HP/OneDrive/Desktop/.vscode/gen ai/.env", 
override=True)

sys.path.append("c:/Users/HP/OneDrive/Desktop/.vscode/gen ai/backend")

from app.db.session import AsyncSessionLocal, engine
from app.models.user import User
from app.models.project import Project
from app.models.chat import ChatSession
from app.models.pdf import PDF
from sqlalchemy.future import select

from app.services.chat_engine import ChatEngine
from app.services.chat_service import ChatService


async def main():
    async with AsyncSessionLocal() as db:
        # Create a real test user seamlessly avoiding locks
        user = User(email=f"verify_{uuid4()}@test.com", clerk_id=f"id_{uuid4()}")
        db.add(user)
        await db.commit()
        await db.refresh(user)


        # Create project and session
        new_proj = Project(name="Verification Decomposition Project", description="", user_id=user.id)
        db.add(new_proj)
        await db.commit()
        await db.refresh(new_proj)

        new_sess = ChatSession(project_id=new_proj.id, user_id=user.id, title="Decomp Task")
        db.add(new_sess)
        await db.commit()
        await db.refresh(new_sess)
        
        # We need two "real indexed documents"
        doc1 = PDF(project_id=new_proj.id, filename="Microservices_Architecture_A.pdf", original_name="Microservices_Architecture_A.pdf", file_path="mock/a.pdf", file_hash=str(uuid4()), status="ready")
        doc2 = PDF(project_id=new_proj.id, filename="Latency_Benchmarks_B.pdf", original_name="Latency_Benchmarks_B.pdf", file_path="mock/b.pdf", file_hash=str(uuid4()), status="ready")
        db.add_all([doc1, doc2])
        await db.commit()
        await db.refresh(doc1)
        await db.refresh(doc2)

        session_id = new_sess.id
        pdf_ids = [doc1.id, doc2.id]
        project_id = new_proj.id

        chat_service = ChatService(db)
        chat_engine_instance = ChatEngine(chat_service)

    # We do NOT mock `_decompose_query` or `_classify_query`.
    # Let Gemini process it entirely!
    
    query = "Synthesize the main differences in architecture proposed in Microservices_Architecture_A.pdf and Latency_Benchmarks_B.pdf and explain the trade-offs in depth."
    print("--- SENDING COMPLEX QUERY ---")
    print(f"Query: {query}")
    
    gen = chat_engine_instance.stream_chat(user_id=user.id, session_id=session_id, project_id=project_id, message=query, pdf_ids=pdf_ids)
    
    async for chunk in gen:
        if "token" in chunk or "status" in chunk:
            print("STREAM:", chunk.strip())

    print("\n--- FETCHING PERSISTED DATABASE ROWS ---")
    from app.models.research import ResearchRun, ResearchStep
    async with AsyncSessionLocal() as db:
        run_res = await db.execute(select(ResearchRun).where(ResearchRun.session_id == session_id))
        run = run_res.scalar_one_or_none()
        if not run:
            print("[FAIL] ResearchRun was not created.")
            sys.exit(1)
            
        print(f"[PASS] Created ResearchRun id: {run.id}, Status: {run.status}")
        
        step_res = await db.execute(select(ResearchStep).where(ResearchStep.run_id == run.id).order_by(ResearchStep.step_order))
        steps = step_res.scalars().all()
        
        if not steps:
            print("[FAIL] ResearchSteps were not created.")
            sys.exit(1)
            
        if len(steps) > 1:
            print("[PASS] Multiple distinct executable steps were generated.")
        else:
            print("[FAIL] Only 1 or 0 steps generated. Not a multi-step distinct breakdown.")
            
        for step in steps:
            print(f" - [{step.step_order}] TYPE: {step.step_type} | DESC: {step.description}")
            if step.step_type not in ["retrieval", "analysis", "comparison", "verification", "synthesis"]:
                print(f"[FAIL] Invalid step type: {step.step_type}")
                
        print("\nAll End-to-End Verifications Finished.")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
