import asyncio
from google import genai
from app.core.config import settings
client = genai.Client(api_key=settings.GEMINI_API_KEY)
def list_m():
    for m in client.models.list():
        if "flash" in m.name:
            print(m.name)
        elif "pro" in m.name:
            print(m.name)
list_m()
