"""
rag — RAG Pipeline Package
Splits chunking, embedding, indexing, and retrieval into separate modules.
"""

from pathlib import Path

KNOWLEDGE_BASE_DIR = Path(__file__).parent.parent / "knowledge_base"
FAISS_INDEX_PATH = Path(__file__).parent.parent / "faiss_index"

from rag.chunking import load_all_chunks, chunk_text
from rag.embedding import get_embeddings
from rag.build_index import build_vectorstore, ensure_vectorstore
from rag.retrieve import retrieve, format_context

__all__ = [
    "KNOWLEDGE_BASE_DIR",
    "FAISS_INDEX_PATH",
    "load_all_chunks",
    "chunk_text",
    "get_embeddings",
    "build_vectorstore",
    "ensure_vectorstore",
    "retrieve",
    "format_context",
]
