import asyncio
import json
import httpx
import os
import sys
import uuid

# Inject backend path explicitly
sys.path.append(os.path.join(os.getcwd(), 'backend'))

async def main():
    import asyncpg
    # Construct DB URL natively mapping standard credentials
    conn = await asyncpg.connect("postgresql://postgres:postgres@localhost:5432/researchos")
    
    # 1. Evaluate Project A logic bounds explicitly 
    proj_a = await conn.fetchrow("SELECT id, user_id FROM projects ORDER BY created_at DESC LIMIT 1")
    if not proj_a:
        print("ERROR: No project detected structurally.")
        return
        
    sess_a = await conn.fetchrow("SELECT id FROM chat_sessions WHERE project_id = $1 LIMIT 1", proj_a['id'])
    if not sess_a:
        sess_id = uuid.uuid4()
        await conn.execute("INSERT INTO chat_sessions (id, user_id, project_id, title) VALUES ($1, $2, $3, 'Diagnostic')", sess_id, proj_a['user_id'], proj_a['id'])
        sess_a = {'id': sess_id}
        
    print(f"Project A Target: {proj_a['id']} | Session A Target: {sess_a['id']}")
    
    # 2. Invoke SSE endpoint safely bounding MOCK_TOKEN parameters natively
    headers = {"Authorization": "Bearer MOCK_TOKEN"}
    payload = {
        "session_id": str(sess_a['id']),
        "project_id": str(proj_a['id']),
        "message": "What is this document about? Please cite."
    }
    
    print("Initializing streaming request payload structurally...")
    full_text = ""
    async with httpx.AsyncClient(timeout=30.0) as client:
        async with client.stream("POST", "http://localhost:8000/chat/stream", json=payload, headers=headers) as response:
             async for line in response.aiter_lines():
                if line.startswith('data: '):
                    try:
                        data_json = json.loads(line[6:])
                        if data_json.get('type') == 'token':
                            full_text += data_json['content']
                    except Exception:
                        pass
                                
    print(f"Stream output securely parsed (Token Count Derived: {len(full_text)} bytes): {full_text[:50]}...")
    
    # 3. Analyze PostgreSQL schema explicitly checking JSONB Sources mapping
    msgs = await conn.fetch("SELECT role, sources FROM chat_messages WHERE session_id = $1 ORDER BY created_at DESC LIMIT 1", sess_a['id'])
    if msgs and msgs[0]['role'] == 'assistant' and msgs[0]['sources'] is not None:
        print("PERSISTENCE SUCCESS: Evaluated model response + JSONB Sources securely mapped into PostgreSQL bounds.")
    else:
        print("PERSISTENCE FAILED: Assistant response or JSONB Sources missing from DB instance.")
        
    # 4. Assess Strict Isolation Architecture resolving Vector Space explicitly 
    from app.services.vector_store import VectorStoreService
    from app.services.embeddings import EmbeddingService
    
    print("Testing namespace boundary isolation globally...")
    emb = EmbeddingService().generate_embeddings(["test concept"])[0]
    vs = VectorStoreService()
    
    # Fabricate disjoint UUID mapping
    proj_b_id = str(uuid.uuid4())
    results = vs.search(project_id=proj_b_id, query_vector=emb, limit=5)
    if len(results) == 0:
        print(f"ISOLATION SUCCESS: Disjoint Project ID {proj_b_id} resulted in 0 chunk collisions globally.")
    else:
        print("ISOLATION FAILED: Cross-project context leakage detected structurally.")
        
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main()) 
