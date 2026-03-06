"""
chunking.py — Document Splitting
Methods to load knowledge base files and split text into manageable overlapping chunks.
"""

import hashlib
from typing import List, Dict

# Need to import KNOWLEDGE_BASE_DIR from the parent __init__
from rag import KNOWLEDGE_BASE_DIR

CHUNK_SIZE = 300       # words per chunk
CHUNK_OVERLAP = 50     # overlap in words


def chunk_text(text: str, source: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[Dict]:
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk_text_str = " ".join(words[start:end])
        chunks.append({
            "content": chunk_text_str,
            "source": source,
            "chunk_id": hashlib.md5(chunk_text_str.encode()).hexdigest()[:8]
        })
        if end == len(words):
            break
        start += chunk_size - overlap
    return chunks


def load_all_chunks() -> List[Dict]:
    """Load and chunk all documents from the knowledge base."""
    all_chunks = []
    for txt_file in KNOWLEDGE_BASE_DIR.glob("*.txt"):
        text = txt_file.read_text(encoding="utf-8")
        chunks = chunk_text(text, source=txt_file.name)
        all_chunks.extend(chunks)
    return all_chunks
