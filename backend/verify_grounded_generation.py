import asyncio
import json
import httpx
import os
import sys
import uuid

sys.path.append(os.path.join(os.getcwd(), 'backend'))

async def test_query(conn, proj_id, sess_id, query, description):
    print(f"\n--- Testing: {description} ---", flush=True)
    headers = {"Authorization": "Bearer MOCK_TOKEN"}
    payload = {
        "session_id": str(sess_id),
        "project_id": str(proj_id),
        "message": query,
        "pdf_ids": []
    }
    
    full_text = ""
    print("Calling /chat/stream...", flush=True)
    async with httpx.AsyncClient(timeout=30.0) as client:
        async with client.stream("POST", "http://localhost:8000/chat/stream", json=payload, headers=headers) as response:
             print("Stream connected, iterating lines...", flush=True)
             async for line in response.aiter_lines():
                print(f"Received line chunk: {line[:50]}", flush=True)
                if line.startswith('data: '):
                    try:
                        data_json = json.loads(line[6:])
                        if data_json.get('type') == 'token':
                            full_text += data_json['content']
                        elif data_json.get('type') == 'done':
                            print("Done received.", flush=True)
                            break
                    except Exception as e:
                        pass
                                
    print(f"Response:\n{full_text}\n", flush=True)
    return full_text

async def main():
    import asyncpg
    print("Connecting to DB...", flush=True)
    conn = await asyncpg.connect("postgresql://postgres:postgrespassword@127.0.0.1:5432/research_db", timeout=5.0)
    print("Connected.", flush=True)
    
    proj_a = await conn.fetchrow("SELECT id, user_id FROM projects ORDER BY created_at DESC LIMIT 1")
    if not proj_a:
        print("ERROR: No project detected.", flush=True)
        return
        
    sess_a = await conn.fetchrow("SELECT id FROM chat_sessions WHERE project_id = $1 LIMIT 1", proj_a['id'])
    if not sess_a:
        sess_id = uuid.uuid4()
        await conn.execute("INSERT INTO chat_sessions (id, user_id, project_id, title) VALUES ($1, $2, $3, 'Diagnostic')", sess_id, proj_a['user_id'], proj_a['id'])
        sess_a = {'id': sess_id}
        
    print(f"Project Target: {proj_a['id']} | Session Target: {sess_a['id']}", flush=True)
    
    print("First query start...", flush=True)
    await test_query(conn, proj_a['id'], sess_a['id'], "What is this document about? Please describe the content and cite sources.", "In corpus question")
    print("Second query start...", flush=True)
    await test_query(conn, proj_a['id'], sess_a['id'], "What is the capital of France?", "Out of corpus question")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
