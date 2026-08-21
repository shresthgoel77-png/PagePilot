import os
import sys
from dotenv import dotenv_values

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
env_dict = dotenv_values(dotenv_path)
if "GEMINI_API_KEY" in env_dict:
    os.environ["GEMINI_API_KEY"] = env_dict["GEMINI_API_KEY"].strip()

from app.core.config import settings
from google import genai
from google.genai import types

def safe_fingerprint(key):
    if not key:
        return "None"
    return f"{key[:4]}...{key[-4:]} (len: {len(key)})"

def test_minimal():
    key = settings.GEMINI_API_KEY
    print(f"settings.GEMINI_API_KEY: {safe_fingerprint(key)}")
    
    env_gemini = os.getenv("GEMINI_API_KEY")
    print(f"os.getenv('GEMINI_API_KEY'): {safe_fingerprint(env_gemini)}")
    
    env_google = os.getenv("GOOGLE_API_KEY")
    print(f"os.getenv('GOOGLE_API_KEY'): {safe_fingerprint(env_google)}")

    print(f"\nInitializing genai.Client(api_key=settings.GEMINI_API_KEY)")
    client = genai.Client(api_key=key)
    
    try:
        print("Testing generate_content(gemini-2.5-flash)...")
        res = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Say hello"
        )
        print("Success! Response:", res.text)
    except Exception as e:
        print("Failed generate_content:", repr(e))

    try:
        print("\nTesting embed_content(text-embedding-004)...")
        res = client.models.embed_content(
            model="text-embedding-004",
            contents="Say hello"
        )
        print("Success! Embedding length:", len(res.embeddings[0].values))
    except Exception as e:
        print("Failed embed_content:", repr(e))
        
    try:
        print("\nTesting fallback HTTP environment variables client defaults...")
        client_auto = genai.Client()
        res = client_auto.models.embed_content(
            model="text-embedding-004",
            contents="Say hello"
        )
        print("Success with auto client!")
    except Exception as e:
        print("Failed auto client:", repr(e))

if __name__ == "__main__":
    test_minimal()
