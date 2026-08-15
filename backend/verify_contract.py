"""Verify backend API contract against running server with real Clerk auth."""
import asyncio
import io
import json
import os
import sys
import httpx

BASE = os.environ.get("API_BASE", "http://localhost:8000")
CLERK_SECRET = os.environ.get("CLERK_SECRET_KEY", "")

RESULTS: list[dict] = []


def record(name: str, ok: bool, status: int | None, detail: str = ""):
    RESULTS.append({"endpoint": name, "ok": ok, "status": status, "detail": detail[:300]})
    mark = "PASS" if ok else "FAIL"
    print(f"[{mark}] {name} -> {status} {detail[:120]}")


async def get_clerk_token() -> str:
    if not CLERK_SECRET:
        raise RuntimeError("CLERK_SECRET_KEY not set")
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.clerk.com/v1/testing_tokens",
            headers={"Authorization": f"Bearer {CLERK_SECRET}"},
        )
        resp.raise_for_status()
        return resp.json()["token"]


async def main():
    print(f"Verifying API at {BASE}\n")

    # --- Health (no auth) ---
    async with httpx.AsyncClient(base_url=BASE, timeout=60.0) as client:
        r = await client.get("/health")
        record("GET /health", r.status_code == 200 and r.json().get("status") == "ok", r.status_code, r.text)

        r = await client.get("/health/deep")
        record(
            "GET /health/deep",
            r.status_code == 200 and r.json().get("status") == "healthy",
            r.status_code,
            r.text,
        )

        # --- Auth required without token ---
        r = await client.get("/projects/")
        record("GET /projects/ (no auth)", r.status_code == 401, r.status_code, r.text)

        try:
            token = await get_clerk_token()
        except Exception as e:
            print(f"FATAL: Could not obtain Clerk testing token: {e}")
            sys.exit(1)

        auth = {"Authorization": f"Bearer {token}"}

        # --- Projects CRUD ---
        r = await client.post("/projects/", headers=auth, json={"name": "Contract Test", "description": "verify"})
        record("POST /projects/", r.status_code == 201, r.status_code, r.text)
        if r.status_code != 201:
            print(json.dumps(RESULTS, indent=2))
            sys.exit(1)
        project = r.json()
        pid = project["id"]

        r = await client.get("/projects/", headers=auth)
        record("GET /projects/", r.status_code == 200 and isinstance(r.json(), list), r.status_code)

        r = await client.get(f"/projects/{pid}", headers=auth)
        record("GET /projects/{id}", r.status_code == 200 and r.json()["id"] == pid, r.status_code)

        r = await client.put(f"/projects/{pid}", headers=auth, json={"name": "Contract Test Updated"})
        record("PUT /projects/{id}", r.status_code == 200, r.status_code)

        # --- PDF upload/list/status ---
        pdf_bytes = b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF"
        files = {"file": ("test.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
        r = await client.post(f"/projects/{pid}/pdfs", headers=auth, files=files)
        record("POST /projects/{id}/pdfs", r.status_code == 201, r.status_code, r.text)
        pdf_id = r.json()["id"] if r.status_code == 201 else None
        if pdf_id:
            status_val = r.json().get("status")
            record("PDF initial status", status_val == "uploaded", r.status_code, f"status={status_val}")

        r = await client.get(f"/projects/{pid}/pdfs", headers=auth)
        record("GET /projects/{id}/pdfs", r.status_code == 200 and isinstance(r.json(), list), r.status_code)

        if pdf_id:
            r = await client.get(f"/projects/{pid}/pdfs/{pdf_id}/download", headers=auth)
            record("GET /projects/{id}/pdfs/{pdf_id}/download", r.status_code == 200, r.status_code)

            # No GET single PDF metadata endpoint
            r = await client.get(f"/projects/{pid}/pdfs/{pdf_id}", headers=auth)
            record("GET /projects/{id}/pdfs/{pdf_id} (missing)", r.status_code == 404, r.status_code)

        # --- Chat sessions ---
        r = await client.post("/chat-sessions/", headers=auth, json={"project_id": pid, "title": "Test Session"})
        record("POST /chat-sessions/", r.status_code == 201, r.status_code, r.text)
        session_id = r.json()["id"] if r.status_code == 201 else None

        r = await client.get("/chat-sessions/", headers=auth, params={"project_id": pid})
        record("GET /chat-sessions/?project_id=", r.status_code == 200, r.status_code)

        if session_id:
            r = await client.get(f"/chat-sessions/{session_id}", headers=auth)
            record("GET /chat-sessions/{id}", r.status_code == 200, r.status_code)

            r = await client.put(f"/chat-sessions/{session_id}", headers=auth, json={"title": "Renamed"})
            record("PUT /chat-sessions/{id}", r.status_code == 200, r.status_code)

        # --- Chat stream (SSE) - may fail if GEMINI invalid ---
        if session_id:
            async with client.stream(
                "POST",
                "/chat/stream",
                headers={**auth, "Accept": "text/event-stream"},
                json={"session_id": session_id, "project_id": pid, "message": "Hello"},
                timeout=30.0,
            ) as stream:
                chunks = []
                async for line in stream.aiter_lines():
                    if line.startswith("data:"):
                        chunks.append(line)
                    if len(chunks) >= 2:
                        break
                record(
                    "POST /chat/stream",
                    stream.status_code == 200 and len(chunks) > 0,
                    stream.status_code,
                    chunks[0] if chunks else "no events",
                )

        # --- Gap analysis ---
        r = await client.post(f"/projects/{pid}/gaps", headers=auth, json={"focus_area": "methods"})
        record(
            "POST /projects/{id}/gaps",
            r.status_code in (200, 400),
            r.status_code,
            r.text,
        )

        # --- Reasoning ---
        if pdf_id:
            async with client.stream(
                "POST",
                f"/projects/{pid}/reason",
                headers={**auth, "Accept": "text/event-stream"},
                json={"query": "Compare", "pdf_ids": [pdf_id], "mode": "compare"},
                timeout=30.0,
            ) as stream:
                ok = stream.status_code in (200, 400)
                record("POST /projects/{id}/reason (<2 pdfs)", ok, stream.status_code)

        # --- No current-user endpoint ---
        r = await client.get("/auth/me", headers=auth)
        record("GET /auth/me (missing)", r.status_code == 404, r.status_code)

        r = await client.get("/users/me", headers=auth)
        record("GET /users/me (missing)", r.status_code == 404, r.status_code)

        # --- Cleanup ---
        if session_id:
            r = await client.delete(f"/chat-sessions/{session_id}", headers=auth)
            record("DELETE /chat-sessions/{id}", r.status_code == 204, r.status_code)

        if pdf_id:
            r = await client.delete(f"/projects/{pid}/pdfs/{pdf_id}", headers=auth)
            record("DELETE /projects/{id}/pdfs/{pdf_id}", r.status_code == 204, r.status_code)

        r = await client.delete(f"/projects/{pid}", headers=auth)
        record("DELETE /projects/{id}", r.status_code == 204, r.status_code)

    passed = sum(1 for x in RESULTS if x["ok"])
    print(f"\n--- Summary: {passed}/{len(RESULTS)} checks passed ---")
    with open("verify_results.json", "w") as f:
        json.dump(RESULTS, f, indent=2)


if __name__ == "__main__":
    asyncio.run(main())
