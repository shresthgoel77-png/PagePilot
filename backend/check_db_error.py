import asyncio
from app.db.session import AsyncSessionLocal
from sqlalchemy import select
from app.models.pdf import PDF

async def main():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(PDF).order_by(PDF.created_at.desc()).limit(1))
        pdf = res.scalar_one_or_none()
        if pdf:
            print(f"Error Message: {pdf.error_message}")
        else:
            print("No PDF found.")
        
asyncio.run(main())
