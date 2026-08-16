import urllib.request
import urllib.error

req = urllib.request.Request(
    'http://localhost:8000/projects',
    headers={'Authorization': 'Bearer MOCK_TOKEN'}
)
try:
    response = urllib.request.urlopen(req)
    print("Success:", response.status)
    print(response.read().decode())
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.reason}")
    print(e.read().decode())
except Exception as e:
    print("Error:", str(e))
