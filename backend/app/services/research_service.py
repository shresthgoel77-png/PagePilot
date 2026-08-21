import json
from uuid import UUID
from collections.abc import AsyncGenerator

from sqlalchemy.future import select

from app.models.research import ResearchRun, ResearchStep
from app.db.session import AsyncSessionLocal as async_session

class ResearchService:
    async def create_research_run(self, session_id: UUID, query: str) -> ResearchRun:
        async with async_session() as db:
            run = ResearchRun(session_id=session_id, query=query, status="planning")
            db.add(run)
            await db.commit()
            await db.refresh(run)
            return run

    async def add_research_steps(self, run_id: UUID, steps_data: list[dict]) -> list[ResearchStep]:
        async with async_session() as db:
            steps = []
            for idx, step_dict in enumerate(steps_data):
                step = ResearchStep(
                    run_id=run_id,
                    step_order=idx + 1,
                    step_type=step_dict.get("type", "analysis"),
                    description=step_dict.get("description", ""),
                    status="pending"
                )
                db.add(step)
                steps.append(step)
            await db.commit()
            for step in steps:
                await db.refresh(step)
            return steps

    async def get_run_with_steps(self, run_id: UUID) -> ResearchRun:
        async with async_session() as db:
            stmt = select(ResearchRun).where(ResearchRun.id == run_id)
            result = await db.execute(stmt)
            run = result.scalar_one_or_none()
            if run:
                await db.refresh(run, ["steps"])
            return run
