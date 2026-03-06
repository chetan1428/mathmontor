"""
Quick test script to verify Gemini API is working
"""
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Configure API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ GEMINI_API_KEY not found in .env file")
    print("📝 Please create a .env file from .env.example and add your API key")
    exit(1)

client = genai.Client(api_key=api_key)

print("✓ API key loaded")
print("\n📋 Testing available models...")

# List available models
try:
    models = client.models.list()
    print("\nAvailable Gemini models:")
    for model in models:
        print(f"  • {model.name}")
except Exception as e:
    print(f"❌ Error listing models: {e}")
    exit(1)

print("\n🧪 Testing text generation with gemini-2.5-flash...")

# Test simple generation
try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Solve: 2x + 5 = 15"
    )
    print(f"\n✓ Response: {response.text[:200]}")
    print("\n✅ Gemini API is working correctly!")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
