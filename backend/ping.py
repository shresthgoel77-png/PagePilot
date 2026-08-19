import httpx

def ping():
    try:
        r = httpx.get("http://localhost:8000/docs", timeout=5)
        print("Server up:", r.status_code, flush=True)
    except Exception as e:
        print("Error:", e, flush=True)

if __name__=='__main__':
    ping()
