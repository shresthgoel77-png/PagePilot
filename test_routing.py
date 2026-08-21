import asyncio
import sys
from unittest.mock import AsyncMock, MagicMock

# Make sure backend is in path
sys.path.append("c:/Users/HP/OneDrive/Desktop/.vscode/gen ai/backend")

from app.services.chat_engine import ChatEngine
from app.services.chat_service import ChatService

async def main():
    chat_service_mock = MagicMock(spec=ChatService)
    engine = ChatEngine(chat_service_mock)
    
    engine.client = MagicMock()
    engine.client.aio = MagicMock()
    engine.client.aio.models = AsyncMock()
    
    # Mock for COMPLEX
    mock_resp_complex = MagicMock()
    mock_resp_complex.text = "COMPLEX"
    engine.client.aio.models.generate_content.return_value = mock_resp_complex
    
    res1 = await engine._classify_query("Synthesize the main differences...")
    print(f"Complex Query Classification: {res1}")

    # Mock for SIMPLE
    mock_resp_simple = MagicMock()
    mock_resp_simple.text = "SIMPLE"
    engine.client.aio.models.generate_content.return_value = mock_resp_simple
    
    res2 = await engine._classify_query("What is the title?")
    print(f"Simple Query Classification: {res2}")

if __name__ == "__main__":
    asyncio.run(main())
