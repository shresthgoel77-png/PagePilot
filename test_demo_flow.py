import requests
import time
import sys

BASE_URL = "http://localhost:8000"
HEADERS = {"Authorization": "Bearer MOCK_TOKEN"}

def wait_for_health():
    print("Waiting for backend health...")
    for _ in range(30):
        try:
            r = requests.get(f"{BASE_URL}/health")
            if r.status_code == 200:
                print("Backend is healthy.")
                return
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(2)
    print("Backend failed to become healthy.")
    sys.exit(1)

def test_flow():
    print("1. Testing GET /projects (to trigger JIT user creation)")
    r = requests.get(f"{BASE_URL}/projects", headers=HEADERS)
    r.raise_for_status()
    print("Projects:", r.json())
    
    print("2. Creating a new project")
    r = requests.post(f"{BASE_URL}/projects", headers=HEADERS, json={"name": "Demo Test Project", "description": "e2e demo"})
    r.raise_for_status()
    project = r.json()
    project_id = project['id']
    print(f"Created project: {project_id}")
    
    print("3. Uploading a document")
    pdf_path = "MYsql notes T.pdf"
    with open(pdf_path, "rb") as f:
        r = requests.post(f"{BASE_URL}/projects/{project_id}/pdfs", headers=HEADERS, files={"file": ("MYsql notes T.pdf", f, "application/pdf")})
    r.raise_for_status()
    pdf = r.json()
    print("Upload returned:", pdf)
    
    print("Waiting for document processing to finish...")
    for _ in range(30):
        try:
            r_pdf = requests.get(f"{BASE_URL}/projects/{project_id}/pdfs", headers=HEADERS)
            pdfs = r_pdf.json()
            current_pdf = next((p for p in pdfs if p['id'] == pdf['id']), None)
            if current_pdf and current_pdf.get('status') == 'ready':
                print("Document processing COMPLETE.")
                break
            elif current_pdf and current_pdf.get('status') == 'error':
                print("Document processing FAILED:", current_pdf.get('error_message'))
                sys.exit(1)
        except requests.exceptions.ConnectionError:
            print("Transient network drop, retrying in 2 seconds...")
        time.sleep(2)

    print("4. Creating a chat session")
    r = requests.post(f"{BASE_URL}/chat-sessions/", headers=HEADERS, json={"project_id": project_id})
    r.raise_for_status()
    session = r.json()
    
    print("5. Testing chat flow - Question 1")
    chat_payload = {
        "session_id": session["id"],
        "project_id": project_id,
        "message": "Summarize this database notes PDF.",
        "pdf_ids": [pdf['id']]
    }
    r = requests.post(f"{BASE_URL}/chat/stream", headers=HEADERS, json=chat_payload, stream=True)
    if r.status_code == 200:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                print(chunk.decode('utf-8'), end='')
        print("\nChat 1 complete.")
    else:
        print("Chat 1 failed:", r.status_code, r.text)

    print("6. Testing chat flow - Question 2")
    chat_payload["message"] = "What specific commands are mentioned for modifying tables?"
    r = requests.post(f"{BASE_URL}/chat/stream", headers=HEADERS, json=chat_payload, stream=True)
    if r.status_code == 200:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                print(chunk.decode('utf-8'), end='')
        print("\nChat 2 complete.")
    else:
        print("Chat 2 failed:", r.status_code, r.text)

if __name__ == "__main__":
    wait_for_health()
    test_flow()
    print("ALL TESTS PASSED")
