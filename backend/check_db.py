import asyncio
import asyncpg
import json

async def check():
    conn = await asyncpg.connect('postgresql://postgres:postgrespassword@localhost:5432/research_db')
    rows = await conn.fetch("SELECT id, filename, status, error_message, parsed_text FROM pdfs ORDER BY created_at DESC LIMIT 2")
    for r in rows:
        print(f"[{r['filename']}] STATUS: {r['status']}")
        print(f"ERROR: {r['error_message']}")
        parsed = json.loads(r['parsed_text']) if r['parsed_text'] else None
        if parsed:
            print(f"PAGES: {len(parsed)}")
            print(f"EXAMPLE: {parsed[0]}")
        else:
            print("PAGES: NONE")
        print("----")
    await conn.close()

asyncio.run(check())
