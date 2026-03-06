"""
embedding.py — Dense Embeddings
Handles converting text chunks into vector embeddings via Gemini.
"""

from typing import List

try:
    from google import genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False


def get_embeddings(texts: List[str], api_key: str) -> List[List[float]]:
    """Get embeddings for a list of texts via Gemini API."""
    if not HAS_GENAI:
        raise ImportError("google-genai package is not installed.")
        
    client = genai.Client(api_key=api_key)
    
    embeddings = []
    # Gemini embedding model
    for text in texts:
        result = client.models.embed_content(
            model="models/text-embedding-004",
            contents=text
        )
        embeddings.append(result.embeddings[0].values)
    
    return embeddings
