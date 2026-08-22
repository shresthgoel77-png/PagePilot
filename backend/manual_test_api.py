import requests
resp = requests.post("http://127.0.0.1:8000/auth/register", json={"email": "testrun@example.com", "password": "TestPassword123!"})
print(resp.status_code)
print(resp.text)
