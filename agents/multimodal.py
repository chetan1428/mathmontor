"""
multimodal.py — Multimodal Extraction (Image + Audio)
Handles extracting math problems from images and transcribing audio.
"""

import os
import re

from google.genai import types
from agents.client import get_client


def extract_from_image(image_bytes: bytes) -> dict:
    """Use Gemini Vision to extract math problem from image."""
    client = get_client()

    # Upload image to Gemini
    from PIL import Image
    import io

    # Detect image format
    img = Image.open(io.BytesIO(image_bytes))

    prompt = (
        "Extract the math problem from this image exactly as written. "
        "If it's handwritten, interpret as best you can. "
        "Return ONLY the problem text — nothing else. "
        "Preserve all mathematical notation, numbers, and variables."
    )

    # Convert PIL Image to bytes for upload
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format=img.format or 'PNG')
    img_byte_arr = img_byte_arr.getvalue()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(data=img_byte_arr, mime_type=f"image/{(img.format or 'png').lower()}"),
            prompt
        ]
    )

    extracted = response.text.strip()

    # Heuristic confidence: longer extraction = more confident
    confidence = min(100, max(40, len(extracted) * 2))
    return {"text": extracted, "confidence": confidence}


def transcribe_audio(audio_bytes: bytes, filename: str = "audio.wav") -> dict:
    """Transcribe audio using Gemini Audio (or fallback to Whisper if needed)."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
        import io
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = filename

        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            prompt="This is a math problem. Preserve all numbers and mathematical terms."
        )
        text = transcript.text.strip()
    except Exception as e:
        # Fallback: return error message
        return {
            "text": "Audio transcription unavailable. Please use text or image input.",
            "confidence": 0,
            "raw_transcript": str(e)
        }

    # Post-process common audio math mishearings
    replacements = {
        "squared": "²",
        "cubed": "³",
        "square root of": "√",
        "to the power of": "^",
        "plus or minus": "±",
        "divided by": "/",
        "multiplied by": "×",
        "times": "×",
        "equals": "=",
        "greater than": ">",
        "less than": "<",
    }
    for phrase, symbol in replacements.items():
        text = re.sub(r'\b' + phrase + r'\b', symbol, text, flags=re.IGNORECASE)

    confidence = min(95, max(50, 70 + len(text) // 10))
    return {"text": text, "confidence": confidence, "raw_transcript": text}
