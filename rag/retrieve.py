"""
retrieve.py — Retrieve & Format
Searches the FAISS vectorstore (with keyword fallback) and formats results for agents.
"""

import os
import pickle
from typing import List, Dict

try:
    from google import genai
    import faiss
    import numpy as np
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False

from rag import FAISS_INDEX_PATH
from rag.chunking import load_all_chunks


def _keyword_retrieve(query: str, top_k: int = 3) -> List[Dict]:
    """
    Fallback: keyword-overlap based retrieval from knowledge base files.
    Works without any embeddings.
    """
    query_words = set(query.lower().split())
    chunks = load_all_chunks()
    scored = []
    for chunk in chunks:
        chunk_words = set(chunk["content"].lower().split())
        score = len(query_words & chunk_words) / max(len(query_words), 1)
        scored.append((score, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for score, chunk in scored[:top_k]:
        c = chunk.copy()
        c["similarity_score"] = score
        results.append(c)
    return results


def retrieve(query: str, top_k: int = 3, api_key: str = None) -> List[Dict]:
    """
    Retrieve top-k relevant chunks for a query.
    Falls back to keyword search if FAISS unavailable.
    """
    if not HAS_FAISS or not (FAISS_INDEX_PATH / "index.faiss").exists():
        return _keyword_retrieve(query, top_k)

    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        return _keyword_retrieve(query, top_k)

    client = genai.Client(api_key=key)

    # Load index + chunks
    index = faiss.read_index(str(FAISS_INDEX_PATH / "index.faiss"))
    with open(FAISS_INDEX_PATH / "chunks.pkl", "rb") as f:
        chunks = pickle.load(f)

    # Embed query
    result = client.models.embed_content(
        model="models/text-embedding-004",
        contents=query
    )
    q_emb = result.embeddings[0].values
    q_arr = np.array([q_emb], dtype=np.float32)
    faiss.normalize_L2(q_arr)

    # Search
    scores, indices = index.search(q_arr, top_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < len(chunks):
            chunk = chunks[idx].copy()
            chunk["similarity_score"] = float(score)
            results.append(chunk)

    return results


def format_context(chunks: List[Dict]) -> str:
    """Format retrieved chunks into a context string for prompts."""
    if not chunks:
        return "No relevant reference material found."
    parts = []
    for i, chunk in enumerate(chunks, 1):
        parts.append(f"[Reference {i} — {chunk['source']}]\n{chunk['content']}")
    return "\n\n".join(parts)
