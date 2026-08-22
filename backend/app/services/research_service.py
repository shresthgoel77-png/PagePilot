import json
import uuid
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy.future import select
from sqlalchemy.orm.attributes import flag_modified

from app.models.research import ResearchRun
from app.db.session import AsyncSessionLocal as async_session

class ResearchService:
    async def create_research_run(self, session_id: UUID, project_id: UUID, user_id: UUID, query: str, mode: str = "complex") -> ResearchRun:
        async with async_session() as db:
            run = ResearchRun(
                session_id=session_id, 
                project_id=project_id,
                user_id=user_id,
                query=query, 
                mode=mode,
                status="running",
                steps_data=[]
            )
            db.add(run)
            await db.commit()
            await db.refresh(run)
            return run

    async def add_research_steps(self, run_id: UUID, steps_data: list[dict]) -> list[dict]:
        async with async_session() as db:
            stmt = select(ResearchRun).where(ResearchRun.id == run_id)
            result = await db.execute(stmt)
            run = result.scalar_one_or_none()
            if not run:
                return []
            
            new_steps = []
            for step_dict in steps_data:
                step_obj = {
                    "id": str(uuid.uuid4()),
                    "type": step_dict.get("type", "analysis"),
                    "description": step_dict.get("description", ""),
                    "status": "queued",
                    "result": None,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                new_steps.append(step_obj)
            
            current_steps = list(run.steps_data) if run.steps_data else []
            current_steps.extend(new_steps)
            run.steps_data = current_steps
            flag_modified(run, "steps_data")
            
            await db.commit()
            return new_steps

    async def get_run(self, run_id: UUID) -> ResearchRun:
        async with async_session() as db:
            stmt = select(ResearchRun).where(ResearchRun.id == run_id)
            result = await db.execute(stmt)
            return result.scalar_one_or_none()

    async def update_research_step(self, run_id: UUID, step_id: str, status: str, result_data: dict = None) -> dict:
        async with async_session() as db:
            stmt = select(ResearchRun).where(ResearchRun.id == run_id)
            res = await db.execute(stmt)
            run = res.scalar_one_or_none()
            if not run or not run.steps_data:
                return None
                
            steps = list(run.steps_data)
            updated_step = None
            for step in steps:
                if step.get("id") == step_id:
                    if status:
                        step["status"] = status
                    if result_data is not None:
                        step["result"] = result_data
                    step["updated_at"] = datetime.now(timezone.utc).isoformat()
                    updated_step = step
                    break
            
            if updated_step:
                run.steps_data = steps
                flag_modified(run, "steps_data")
                run.updated_at = datetime.now(timezone.utc)
                await db.commit()
                
            return updated_step

