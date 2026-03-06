"""
retrieve_similar_problems.py — Retrieval & Query Operations
Functions to find similar problems, get stats, and format memory context.
"""

import sqlite3
import json
from typing import List, Dict

from memory.db_init import DB_PATH, init_db


def find_similar(query: str, top_k: int = 3, topic: str = None) -> List[Dict]:
    """
    Find similar past problems using keyword overlap.
    Optionally filter by topic.
    Returns list of dicts with problem details.
    """
    init_db()
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    if topic:
        rows = conn.execute(
            "SELECT * FROM problems WHERE topic = ? ORDER BY created_at DESC LIMIT 100",
            (topic,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM problems ORDER BY created_at DESC LIMIT 100"
        ).fetchall()
    conn.close()

    if not rows:
        return []

    query_words = set(query.lower().split())
    scored = []
    for row in rows:
        row_dict = dict(row)
        text = (row_dict.get("input_text", "") + " " +
                row_dict.get("answer", "")).lower()
        row_words = set(text.split())
        overlap = len(query_words & row_words)
        union = len(query_words | row_words)
        jaccard = overlap / union if union > 0 else 0
        scored.append((jaccard, row_dict))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for score, row in scored[:top_k]:
        if score > 0:
            row["similarity"] = round(score, 3)
            try:
                row["parsed"] = json.loads(row.get("parsed_json") or "{}")
            except Exception:
                row["parsed"] = {}
            results.append(row)
    return results


def get_ocr_corrections() -> List[Dict]:
    """Get all stored OCR corrections for rule-based pre-processing."""
    init_db()
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM ocr_corrections ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_problems(limit: int = 50) -> List[Dict]:
    """Retrieve recent problems from memory (for UI history view)."""
    init_db()
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM problems ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_stats() -> Dict:
    """Return memory statistics."""
    init_db()
    conn = sqlite3.connect(str(DB_PATH))
    total = conn.execute("SELECT COUNT(*) FROM problems").fetchone()[0]
    correct = conn.execute("SELECT COUNT(*) FROM problems WHERE feedback='correct'").fetchone()[0]
    incorrect = conn.execute("SELECT COUNT(*) FROM problems WHERE feedback='incorrect'").fetchone()[0]
    topics = conn.execute(
        "SELECT topic, COUNT(*) as cnt FROM problems GROUP BY topic ORDER BY cnt DESC"
    ).fetchall()
    conn.close()
    return {
        "total": total,
        "correct": correct,
        "incorrect": incorrect,
        "unevaluated": total - correct - incorrect,
        "topics": {row[0]: row[1] for row in topics}
    }


def format_memory_context(similar_problems: List[Dict]) -> str:
    """Format similar problems into a context string for agents."""
    if not similar_problems:
        return ""
    parts = ["=== Similar Past Problems (from memory) ==="]
    for i, p in enumerate(similar_problems, 1):
        parts.append(
            f"\n[Memory {i}] Problem: {p.get('input_text', '')[:200]}\n"
            f"Answer: {p.get('answer', '')[:300]}\n"
            f"Feedback: {p.get('feedback', 'none')} | "
            f"Confidence: {p.get('confidence', 0)}%"
        )
    return "\n".join(parts)
