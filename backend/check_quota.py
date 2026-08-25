import asyncio
from google import genai
from app.core.config import settings

async def main():
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Hello world!"
    )
    print(response.text)

if __name__ == "__main__":
    asyncio.run(main())
