"""
build_index.py — Build & Save FAISS Index
Handles indexing embedded chunks into FAISS and saving the metadata correctly.
"""

import os
import pickle
from typing import List, Dict

try:
    import faiss
    import numpy as np
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False

from rag import FAISS_INDEX_PATH
from rag.chunking import load_all_chunks
from rag.embedding import get_embeddings


def build_vectorstore(api_key: str = None) -> bool:
    """
    Build the FAISS index from all knowledge base documents.
    Saves index + chunk metadata to disk.
    Returns True on success.
    """
    if not HAS_FAISS:
        print("FAISS not available — skipping vectorstore build")
        return False

    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        print("No GEMINI_API_KEY — cannot build vectorstore")
        return False

    chunks = load_all_chunks()
    if not chunks:
        print("No knowledge base documents found!")
        return False

    print(f"Embedding {len(chunks)} chunks...")
    texts = [c["content"] for c in chunks]

    # Embed in batches
    all_embeddings = []
    batch_size = 100
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}...")
        embs = get_embeddings(batch, key)
        all_embeddings.extend(embs)

    dim = len(all_embeddings[0])
    index = faiss.IndexFlatIP(dim)  # Inner product (cosine with normalized vecs)

    # Normalize for cosine similarity
    emb_array = np.array(all_embeddings, dtype=np.float32)
    faiss.normalize_L2(emb_array)
    index.add(emb_array)

    # Save
    FAISS_INDEX_PATH.mkdir(exist_ok=True)
    faiss.write_index(index, str(FAISS_INDEX_PATH / "index.faiss"))
    with open(FAISS_INDEX_PATH / "chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)

    print(f"Vectorstore built: {len(chunks)} chunks indexed.")
    return True


def ensure_vectorstore(api_key: str = None) -> str:
    """Build vectorstore if it doesn't exist. Returns status message."""
    if not HAS_FAISS:
        return "Using keyword search (FAISS not installed)"
    if (FAISS_INDEX_PATH / "index.faiss").exists():
        return "Vectorstore ready ✓"
    success = build_vectorstore(api_key)
    return "Vectorstore built ✓" if success else "Vectorstore build failed — using keyword search"
