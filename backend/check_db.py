import asyncio, json
from app.db.session import AsyncSessionLocal as async_session
from app.models.research import ResearchStep
from sqlalchemy.future import select

async def fetch_steps():
    async with async_session() as db:
        res = await db.execute(select(ResearchStep))
        steps = res.scalars().all()
        print(json.dumps([{'order': s.step_order, 'type': s.step_type, 'desc': s.description} for s in steps], indent=2))

if __name__ == "__main__":
    asyncio.run(fetch_steps())
