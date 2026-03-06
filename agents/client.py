"""
client.py — Gemini API Client & Helper
Configures and wraps calls to the Gemini API.
"""

import os

from google import genai
from google.genai import types


def get_client():
    """Configure Gemini API."""
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("GEMINI_API_KEY not set in environment")
    return genai.Client(api_key=key)


def call_gemini(system: str, user: str, model: str = "gemini-2.5-flash",
                response_format: str = "text", temperature: float = 0.2) -> str:
    """Single Gemini call helper."""
    client = get_client()

    # Combine system and user prompts for Gemini
    full_prompt = f"{system}\n\n{user}"

    config = types.GenerateContentConfig(
        temperature=temperature,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="application/json" if response_format == "json" else "text/plain"
    )

    response = client.models.generate_content(
        model=model,
        contents=full_prompt,
        config=config
    )

    return response.text.strip()
